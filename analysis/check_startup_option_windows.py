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
        mode=sys.argv[2] if len(sys.argv)>2 else 'view'
        mode_label=mode
        if mode.startswith('view'):mode='view'
        u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
        def find_caption(parent,caption):
            matches=[]
            @CB
            def child(hwnd,param):
                if text(hwnd).replace('&','')==caption:matches.append(hwnd)
                return True
            u.EnumChildWindows(parent,child,0)
            assert len(matches)==1,(caption,matches)
            return matches[0]
        def string_at(ptr):
            if not ptr:return ''
            length=read32(ptr-4)
            if not length or length>2000:return ''
            buf=c.create_string_buffer(length);assert k.ReadProcessMemory(pi.process,ptr,buf,length,None)
            return buf.raw.decode('latin1')
        time.sleep(5)
        form=read32(base+0x1c8964);assert form
        main_hwnd=read32(form+0x14c)
        from capture_window import capture
        capture(main_hwnd,work/(exe.stem+'_'+mode_label+'_startup.png'))
        manifest=json.loads((Path(__file__).parent/'startup_hint_option_manifest.json').read_text());flag=base+manifest['rva']+manifest['symbols']['enabled']
        initial_enabled=read32(flag)&255
        if '--expect-off' in sys.argv:assert initial_enabled==0
        if '--expect-on' in sys.argv:assert initial_enabled==1
        ini=read32(form+0xc4c);ini_path=string_at(read32(ini+4))
        u.PostMessageW(find_caption(main_hwnd,'Setup'),0xf5,0,0);time.sleep(1)
        setup=read32(read32(base+0x1b1b58));hwnd=read32(setup+0x14c)
        checkbox=find_caption(hwnd,'Show startup text')
        initial_checked=u.SendMessageW(checkbox,0xf0,0,0)
        assert initial_checked==initial_enabled,(initial_checked,initial_enabled)
        capture(hwnd,work/(exe.stem+'_'+mode_label+'_setup.png'))
        if mode in ('off','off_cancel','on'):
            desired=1 if mode=='on' else 0
            if initial_checked!=desired:u.SendMessageW(checkbox,0xf5,0,0)
            assert u.SendMessageW(checkbox,0xf0,0,0)==desired
        u.PostMessageW(find_caption(hwnd,'Cancel' if mode in ('view','off_cancel') else 'OK'),0xf5,0,0)
        time.sleep(2)
        after_enabled=read32(flag)&255
        if after_enabled!=(initial_enabled if mode in ('view','off_cancel') else int(mode=='on')):
            print('DIAG',after_enabled,'setup visible',u.IsWindowVisible(hwnd),flush=True)
            capture(hwnd,work/(exe.stem+'_save_failure.png'))
            errors=[]
            @CB
            def error_window(ew,param):
                pid=w.DWORD();u.GetWindowThreadProcessId(ew,c.byref(pid))
                if pid.value==pi.pid and u.IsWindowVisible(ew):
                    captions=[]
                    @CB
                    def error_child(ch,param):
                        captions.append(text(ch));return True
                    u.EnumChildWindows(ew,error_child,0);errors.append(dict(title=text(ew),children=captions))
                return True
            u.EnumDesktopWindows(desk,error_window,0);print(errors,flush=True)
            time.sleep(4);after_enabled=read32(flag)&255
        assert after_enabled==(initial_enabled if mode in ('view','off_cancel') else int(mode=='on'))
        import winreg
        registry_path=r'Software\MHP\SdInstr\Comm'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,registry_path,0,winreg.KEY_READ|winreg.KEY_WOW64_32KEY) as registry:
            try:stored=winreg.QueryValueEx(registry,'ShowStartupText')[0]
            except FileNotFoundError:stored=None
        if mode in ('off','on'):assert stored==int(mode=='on'),stored
        entries=[] if stored is None else ['ShowStartupText='+str(stored)]
        import hashlib
        report=dict(result='PASS',sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),mode=mode_label,registry_path=registry_path,initial_enabled=initial_enabled,initial_checked=initial_checked,after_enabled=after_enabled,ini_path=ini_path,ini_entries=entries)
        (work/(exe.stem+'_'+mode_label+'.json')).write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2))
    finally:
        k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000)
        k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)

if __name__=='__main__': check(Path(sys.argv[1]).resolve())
