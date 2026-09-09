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
        for second in range(8):
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
            hint_manifest=json.loads((Path(__file__).parent/'startup_wake_hint_manifest.json').read_text())
            at=base+hint_manifest['rva'];sy=hint_manifest['symbols']
            snapshot['hint_state']=read32(at+sy['state'])&255
            snapshot['received']=read32(at+sy['received'])&255
            if second in (0,4,7):
                from capture_window import capture
                capture(read32(form+0x14c),work/(exe.stem+'_hint_'+str(second+1)+'.png'))
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
