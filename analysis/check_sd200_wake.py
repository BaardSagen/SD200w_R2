"""Run an isolated GUI instance on a private Windows desktop and inspect startup."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import json, time, sys

class SI(c.Structure):
    _fields_=[('cb',w.DWORD),('reserved',w.LPWSTR),('desktop',w.LPWSTR),('title',w.LPWSTR),
              ('x',w.DWORD),('y',w.DWORD),('cx',w.DWORD),('cy',w.DWORD),('charsx',w.DWORD),('charsy',w.DWORD),
              ('fill',w.DWORD),('flags',w.DWORD),('show',w.WORD),('reservedsize',w.WORD),('reservedbytes',c.c_void_p),
              ('stdin',w.HANDLE),('stdout',w.HANDLE),('stderr',w.HANDLE)]
class PI(c.Structure):
    _fields_=[('process',w.HANDLE),('thread',w.HANDLE),('pid',w.DWORD),('tid',w.DWORD)]
k=c.WinDLL('kernel32',use_last_error=True)
u=c.WinDLL('user32',use_last_error=True)
n=c.WinDLL('ntdll')
CB=c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.CreateDesktopW.argtypes=[w.LPCWSTR,c.c_void_p,c.c_void_p,w.DWORD,w.DWORD,c.c_void_p];u.CreateDesktopW.restype=w.HANDLE
u.CloseDesktop.argtypes=[w.HANDLE]
u.EnumDesktopWindows.argtypes=[w.HANDLE,CB,w.LPARAM]
u.EnumChildWindows.argtypes=[w.HWND,CB,w.LPARAM]
u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,c.c_int]
u.GetClassNameW.argtypes=[w.HWND,w.LPWSTR,c.c_int]
u.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
u.IsWindowVisible.argtypes=[w.HWND];u.IsWindowVisible.restype=w.BOOL
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
k.CreateProcessW.argtypes=[w.LPCWSTR,w.LPWSTR,c.c_void_p,c.c_void_p,w.BOOL,w.DWORD,c.c_void_p,w.LPCWSTR,c.POINTER(SI),c.POINTER(PI)]
k.CreateProcessW.restype=w.BOOL
k.TerminateProcess.argtypes=[w.HANDLE,w.UINT]
k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD]
k.CloseHandle.argtypes=[w.HANDLE]
k.ReadProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)]
k.GetExitCodeProcess.argtypes=[w.HANDLE,c.POINTER(w.DWORD)]
n.NtQueryInformationProcess.argtypes=[w.HANDLE,w.ULONG,c.c_void_p,w.ULONG,c.c_void_p]

def check(exe):
    live_rows='--live-rows' in sys.argv
    desktop_name='SD200W_startup_test_'+str(time.time_ns())
    desk=u.CreateDesktopW(desktop_name,None,None,0,0x1ff,None)
    if not desk: raise c.WinError(c.get_last_error())
    si=SI();si.cb=c.sizeof(si);si.desktop=desktop_name;si.flags=1;si.show=0
    if live_rows:
        u.CloseDesktop(desk)
        u.OpenInputDesktop.argtypes=[w.DWORD,w.BOOL,w.DWORD];u.OpenInputDesktop.restype=w.HANDLE
        desk=u.OpenInputDesktop(0,False,0x1ff)
        assert desk
        si.desktop='winsta0\\default';si.show=1
    pi=PI()
    work=Path(__file__).resolve().parent/'runtime_test'
    work.mkdir(exist_ok=True)
    if not k.CreateProcessW(str(exe),None,None,None,False,0,None,str(work),c.byref(si),c.byref(pi)):
        u.CloseDesktop(desk);raise c.WinError(c.get_last_error())
    try:
        def read32(address):
            value=w.DWORD();done=c.c_size_t()
            if not k.ReadProcessMemory(pi.process,address,c.byref(value),4,c.byref(done)): return None
            return value.value
        peb=c.c_size_t()
        assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0
        base=read32(peb.value+8)
        def text(hwnd,cls=False):
            buf=c.create_unicode_buffer(1024)
            (u.GetClassNameW if cls else u.GetWindowTextW)(hwnd,buf,1024)
            return buf.value
        snapshots=[]
        actions=[]
        for second in range(57 if "--wake-test" in sys.argv else 4 if '--look-only' in sys.argv else 22 if live_rows else 12):
            time.sleep(1)
            windows=[]
            @CB
            def enum(hwnd,param):
                pid=w.DWORD();u.GetWindowThreadProcessId(hwnd,c.byref(pid))
                if pid.value==pi.pid:
                    children=[]
                    @CB
                    def child(ch,param):
                        caption=text(ch)
                        if caption: children.append(caption)
                        return True
                    u.EnumChildWindows(hwnd,child,0)
                    windows.append(dict(title=text(hwnd),cls=text(hwnd,True),visible=bool(u.IsWindowVisible(hwnd)),children=children))
                return True
            u.EnumDesktopWindows(desk,enum,0)
            form=read32(base+0x1c8964)
            notebook=read32(form+0x30c) if form else None
            page=read32(notebook+0x200) if notebook else None
            status=w.DWORD();k.GetExitCodeProcess(pi.process,c.byref(status))
            snapshot=dict(second=second+1,page=page,exit_code=status.value,windows=windows)
            snapshots.append(snapshot)
            if live_rows and second in (0,3,20):
                from capture_window import capture
                capture(read32(form+0x14c),work/(exe.stem+'_main_'+str(second+1)+'.png'))
            if '--detect' in sys.argv and second==1 and form:
                button=read32(form+0x4ec)
                parent=read32(button+0x24)
                hwnd=read32(parent+0x14c)
                x=read32(button+0x30)+read32(button+0x38)//2
                y=read32(button+0x34)+read32(button+0x3c)//2
                assert hwnd and x<65536 and y<65536
                assert u.PostMessageW(hwnd,0x201,1,x|(y<<16))
                assert u.PostMessageW(hwnd,0x202,0,x|(y<<16))
                actions.append(dict(action='click_detect',second=second+1,x=x,y=y))
            if live_rows and second in (5,8,11,14):
                detection=read32(read32(base+0x1b1e1c))
                if not u.IsWindowVisible(read32(detection+0x14c)):
                    actions.append(dict(action='detection_closed_early',second=second+1))
                    break
                listing=read32(detection+0x2e4)
                inner=read32(listing+0x248)
                lh=read32(inner+0x14c)
                u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
                count=u.SendMessageW(lh,0x18b,0,0)
                lines=[]
                for row in range(max(0,count)):
                    buf=c.create_unicode_buffer(2048)
                    u.SendMessageW(lh,0x189,row,c.addressof(buf))
                    lines.append(buf.value)
                array=read32(detection+0x330)
                states=[]
                for row in range(read32(array-4) if array else 0):
                    obj=read32(array+20*row)
                    states.append(dict(searching=read32(obj+0x60)&255,kind=(read32(obj+0x70)>>8)&255))
                    if '--logger-debug' in sys.argv:
                        def read_string(address):
                            ptr=read32(address)
                            if not ptr:return ''
                            length=min(read32(ptr-4) or 0,2048)
                            buf=c.create_string_buffer(length)
                            k.ReadProcessMemory(pi.process,ptr,buf,length,None)
                            return buf.raw.decode('latin1')
                        states[-1].update(buffer=read_string(obj+0x58),last_line=read_string(obj+0x5c))
                actions.append(dict(action='rows',second=second+1,count=count,lines=lines,states=states))
                if '--select-test' in sys.argv:
                    hidden=[]
                    @CB
                    def check_choices(ch,param):
                        if text(ch) in ('Instrument','Aux','None'):
                            hidden.append((text(ch),bool(u.IsWindowVisible(ch))))
                        return True
                    u.EnumChildWindows(read32(detection+0x14c),check_choices,0)
                    assert not any(v for _,v in hidden),hidden
                    if second in (8,11,14):
                        expected=({8:2,11:0,14:1}[second] if '--select-last' in sys.argv else 1 if second==11 else 0)
                        assert lines[expected].endswith(';Instr'),(expected,lines)
                        assert sum(s.endswith(';Instr') for s in lines)==1,lines
                    if second==14:
                        if '--select-ok' in sys.argv:
                            u.PostMessageW(read32(read32(detection+0x2d0)+0x14c),0xf5,0,0)
                            actions.append(dict(action='accept_ok',expected_port='Com11' if '--select-last' in sys.argv else 'Com7'))
                        else:
                            dy=24 if '--select-last' in sys.argv else 8
                            u.PostMessageW(lh,0x203,1,20|(dy<<16))
                            u.PostMessageW(lh,0x202,0,20|(dy<<16))
                            actions.append(dict(action='accept_double_click',expected_port='Com11' if '--select-last' in sys.argv else 'Com7'))
                from capture_window import capture
                capture(read32(detection+0x14c),work/(exe.stem+'_'+str(second+1)+'.png'))
                if second in (5,8,11):
                    row=0 if second in (5,11) else 1
                    if '--select-last' in sys.argv:row={5:2,8:0,11:1}[second]
                    y=8+16*row
                    u.PostMessageW(lh,0x201,1,20|(y<<16));u.PostMessageW(lh,0x202,0,20|(y<<16))
            if '--detect' in sys.argv and second==(17 if live_rows else 5):
                detection=read32(read32(base+0x1b1e1c))
                hwnd=read32(detection+0x14c)
                if '--select-test' in sys.argv:
                    deadline=time.monotonic()+10
                    while u.IsWindowVisible(hwnd) and time.monotonic()<deadline:
                        time.sleep(.2)
                    assert not u.IsWindowVisible(hwnd),'Selection did not close Detect'
                    actions.append(dict(action='selection_closed_detection',passed=True))
                if '--capture' in sys.argv:
                    from capture_window import capture
                    capture(hwnd,work/(exe.stem+'.png'))
                    listing=read32(detection+0x2e4)
                    actions.append(dict(action='result_colors',rows=hex(read32(listing+0x25c)),background=hex(read32(read32(listing+0x248)+0x60))))
                actions.append(dict(action='cancel_detection',visible=bool(u.IsWindowVisible(hwnd)),title=text(hwnd)))
                if u.IsWindowVisible(hwnd):assert u.PostMessageW(hwnd,0x10,0,0)
            if '--detect' in sys.argv and second==(19 if live_rows else 7):
                matches=[]
                @CB
                def find_setup(ch,param):
                    if text(ch).replace('&','')=='Setup':matches.append(ch)
                    return True
                u.EnumChildWindows(read32(form+0x14c),find_setup,0)
                assert len(matches)==1,matches
                assert u.PostMessageW(matches[0],0xf5,0,0)
                actions.append(dict(action='open_normal_setup'))
            if '--detect' in sys.argv and second==(20 if live_rows else 9):
                setup=read32(read32(base+0x1b1b58))
                hwnd=read32(setup+0x14c)
                if live_rows:
                    from capture_window import capture
                    capture(hwnd,work/(exe.stem+'_setup.png'))
                actions.append(dict(action='cancel_normal_setup',visible=bool(u.IsWindowVisible(hwnd)),title=text(hwnd)))
                assert u.PostMessageW(hwnd,0x10,0,0)
            if '--wake-test' in sys.argv:
                comm=read32(form+0x510)
                download=read32(read32(base+0x1b21e0))
                record=dict(action='comm_state',second=second+1,comm=hex(comm or 0),serial_handle=read32(comm+0x2c),baud=read32(comm+0x30),port=(read32(comm+0x34) or 0)&255,
                    flags={hex(o):read32(comm+o) for o in (0x4c,0x50,0x407c,0x4080,0x4094)},download_flags={hex(o):read32(download+o) for o in (0xa60,0xa64,0xa68,0x234)})
                def managed(address):
                    ptr=read32(address)
                    if not ptr:return ''
                    length=min(read32(ptr-4) or 0,256);buf=c.create_string_buffer(length)
                    k.ReadProcessMemory(pi.process,ptr,buf,length,None)
                    return buf.raw.decode('latin1')
                record['typed']=managed(form+0x90c)
                duplicate=w.HANDLE()
                k.DuplicateHandle.argtypes=[w.HANDLE,w.HANDLE,w.HANDLE,c.POINTER(w.HANDLE),w.DWORD,w.BOOL,w.DWORD]
                k.GetCurrentProcess.restype=w.HANDLE
                if k.DuplicateHandle(pi.process,read32(comm+0x2c),k.GetCurrentProcess(),c.byref(duplicate),0,False,2):
                    dcb=c.create_string_buffer(28);c.c_uint.from_buffer(dcb).value=28
                    k.GetCommState.argtypes=[w.HANDLE,c.c_void_p]
                    if k.GetCommState(duplicate,dcb):record['dcb']=list(dcb.raw)
                    stat=c.create_string_buffer(12);err=w.DWORD()
                    k.ClearCommError.argtypes=[w.HANDLE,c.POINTER(w.DWORD),c.c_void_p]
                    if k.ClearCommError(duplicate,c.byref(err),stat):record['comstat']=list(stat.raw)
                    k.CloseHandle(duplicate)
                actions.append(record)
                if second==0:assert record['port']==7,record
                setup_buttons=[]
                @CB
                def get_setup(ch,param):
                    if text(ch).replace('&','')=='Setup':setup_buttons.append(ch)
                    return True
                u.EnumChildWindows(read32(form+0x14c),get_setup,0)
                if second in (21,22,23):
                    for _ in range(24):u.PostMessageW(setup_buttons[0],0x102,ord('I'),1)
                    actions.append(dict(action='stop_before_passive'))
                if second==24:
                    u.PostMessageW(setup_buttons[0],0x102,ord('G'),1)
                if second==25:
                    assert len(setup_buttons)==1
                    u.PostMessageW(setup_buttons[0],0x102,ord('H'),1)
                    actions.append(dict(action='terminal_H'))
                if second==29:
                    button=read32(form+0x374);parent=read32(button+0x24);hwnd=read32(parent+0x14c)
                    u.PostMessageW(read32(button+0x14c),0xf5,0,0)
                    actions.append(dict(action='download_after_H'))
                if second==41:
                    hwnd=read32(download+0x14c)
                    if u.IsWindowVisible(hwnd):
                        cancel=[]
                        @CB
                        def get_cancel(ch,param):
                            if text(ch).replace('&','')=='Cancel':cancel.append(ch)
                            return True
                        u.EnumChildWindows(hwnd,get_cancel,0)
                        assert cancel
                        u.PostMessageW(cancel[0],0xf5,0,0)
                    actions.append(dict(action='cancel_download',visible=bool(u.IsWindowVisible(hwnd))))
                if second in range(44,50):
                    for _ in range(24):u.PostMessageW(setup_buttons[0],0x102,ord('I'),1)
                    actions.append(dict(action='terminal_I_burst'))
                if second in (28,34,40,43,52,55):
                    from capture_window import capture
                    target=read32(download+0x14c) if u.IsWindowVisible(read32(download+0x14c)) else read32(form+0x14c)
                    capture(target,work/(exe.stem+'_wake_'+str(second+1)+'.png'))
            errors=[x for x in windows if x['cls'] in ('TMessageForm','#32770') and any('error' in t.lower() or 'violation' in t.lower() for t in [x['title']]+x['children'])]
            if errors or status.value!=259: break
        report=dict(exe=exe.name,snapshots=snapshots,actions=actions)
        (work/(exe.stem+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(dict(exe=exe.name, observations=len(snapshots),
                              pages=[s['page'] for s in snapshots],actions=actions,
                              visible_dialogs=[win for s in snapshots for win in s['windows']
                                               if win['visible'] and win['cls'] in ('#32770','TMessageForm')]),indent=2),flush=True)
    finally:
        k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000)
        k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)

if __name__=='__main__': check(Path(sys.argv[1]).resolve())
