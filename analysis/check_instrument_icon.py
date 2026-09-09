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


from capture_window import capture
exe=Path('SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe').resolve();si=SI();si.cb=c.sizeof(si);pi=PI()
assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(exe.parent),c.byref(si),c.byref(pi))
try:
 time.sleep(3)
 def read32(addr):
  value=w.DWORD();assert k.ReadProcessMemory(pi.process,addr,c.byref(value),4,None);return value.value
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0
 base=read32(peb.value+8);form=read32(base+0x1c8964);hwnd=read32(form+0x14c)
 capture(hwnd,Path('analysis/runtime_test/instrument_icon_v112.png'))
 u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
 small=u.SendMessageW(hwnd,0x7f,0,0);large=u.SendMessageW(hwnd,0x7f,1,0)
 # Explorer extraction must also recognize the new icon group.
 shell=c.WinDLL('shell32');shell.ExtractIconExW.argtypes=[w.LPCWSTR,c.c_int,c.POINTER(w.HICON),c.POINTER(w.HICON),w.UINT]
 big=w.HICON();little=w.HICON();num=shell.ExtractIconExW(str(exe),0,c.byref(big),c.byref(little),1);assert num==2 and big and little
 u.DestroyIcon.argtypes=[w.HICON];u.DestroyIcon(big);u.DestroyIcon(little)
 Path('analysis/instrument_icon_gui_validation.json').write_text(json.dumps(dict(result='PASS',main_window=hwnd,small_icon=small,large_icon=large,explorer_icon_extracted=True,screenshot='analysis/runtime_test/instrument_icon_v112.png'),indent=2));print('PASS: GUI loaded and Explorer icon extracted')
finally:k.TerminateProcess(pi.process,0);k.CloseHandle(pi.thread);k.CloseHandle(pi.process)
