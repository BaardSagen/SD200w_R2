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


exe=Path('SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe').resolve();si=SI();si.cb=c.sizeof(si);pi=PI()
assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(exe.parent),c.byref(si),c.byref(pi))
try:
 time.sleep(2);found=[]
 @CB
 def enum(hwnd,param):
  pid=w.DWORD();u.GetWindowThreadProcessId(hwnd,c.byref(pid))
  if pid.value==pi.pid:
   title=c.create_unicode_buffer(512);u.GetWindowTextW(hwnd,title,512)
   if title.value.startswith('Find communication speed'):
    rect=w.RECT();u.GetWindowRect(hwnd,c.byref(rect));found.append(dict(title=title.value,width=rect.right-rect.left))
  return True
 u.EnumWindows.argtypes=[CB,w.LPARAM];u.EnumWindows(enum,0)
 assert len(found)==1 and found[0]['title']=='Find communication speed - Double-click green ports to open',found
 # Measure using the actual Windows caption font and leave space for the close button.
 class NCM(c.Structure):
  _fields_=[('cbSize',w.UINT),('metrics',c.c_byte*500)]
 # Use NONCLIENTMETRICSW's caption LOGFONTW at offset 24.
 data=c.create_string_buffer(504);c.cast(data,c.POINTER(w.UINT))[0]=504
 assert u.SystemParametersInfoW(0x29,504,data,0)
 g=c.WinDLL('gdi32');g.CreateFontIndirectW.argtypes=[c.c_void_p];g.CreateFontIndirectW.restype=w.HANDLE
 g.SelectObject.argtypes=[w.HDC,w.HANDLE];g.SelectObject.restype=w.HANDLE;g.DeleteObject.argtypes=[w.HANDLE]
 u.GetDC.argtypes=[w.HWND];u.GetDC.restype=w.HDC;u.ReleaseDC.argtypes=[w.HWND,w.HDC]
 g.GetTextExtentPoint32W.argtypes=[w.HDC,w.LPCWSTR,c.c_int,c.POINTER(w.SIZE)]
 dc=u.GetDC(0);font=g.CreateFontIndirectW(c.addressof(data)+24);old=g.SelectObject(dc,font);size=w.SIZE()
 assert g.GetTextExtentPoint32W(dc,found[0]['title'],len(found[0]['title']),c.byref(size))
 g.SelectObject(dc,old);g.DeleteObject(font);u.ReleaseDC(0,dc)
 found[0]['caption_text_width']=size.cx;assert size.cx+65<=found[0]['width'],found
 Path('analysis/detect_title_gui_validation.json').write_text(json.dumps(dict(result='PASS',windows=found),indent=2));print(found)
finally:k.TerminateProcess(pi.process,0);k.CloseHandle(pi.thread);k.CloseHandle(pi.process)
