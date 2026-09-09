"""Launch the delivered single EXE from an otherwise empty customer folder."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,shutil,json,os
from check_startup_windows import k,u,PI,CB
R=Path(__file__).resolve().parent.parent;M=json.loads((R/'analysis/single_exe_142_manifest.json').read_text())
class Entry(c.Structure):
 _fields_=[('size',w.DWORD),('usage',w.DWORD),('pid',w.DWORD),('heap',c.c_size_t),('module',w.DWORD),('threads',w.DWORD),('parent',w.DWORD),('priority',w.LONG),('flags',w.DWORD),('exe',w.WCHAR*260)]
k.CreateToolhelp32Snapshot.argtypes=[w.DWORD,w.DWORD];k.CreateToolhelp32Snapshot.restype=w.HANDLE
k.Process32FirstW.argtypes=[w.HANDLE,c.POINTER(Entry)];k.Process32NextW.argtypes=[w.HANDLE,c.POINTER(Entry)]
k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
def descendants(parent):
 snap=k.CreateToolhelp32Snapshot(2,0);e=Entry();e.size=c.sizeof(e);found=[]
 try:
  ok=k.Process32FirstW(snap,c.byref(e))
  while ok:
   if e.parent==parent:found.append(e.pid)
   ok=k.Process32NextW(snap,c.byref(e))
 finally:k.CloseHandle(snap)
 return found
def cache():return Path(os.environ['LOCALAPPDATA'])/'SAIV_IT'/M['cache_tag']
def elevation(process):
 a=c.WinDLL('advapi32',use_last_error=True);a.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,c.POINTER(w.HANDLE)];a.GetTokenInformation.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)]
 token=w.HANDLE();assert a.OpenProcessToken(process,8,c.byref(token))
 try:
  value=w.DWORD();size=w.DWORD();assert a.GetTokenInformation(token,20,c.byref(value),4,c.byref(size));return value.value
 finally:k.CloseHandle(token)
def start(si,desk,out):
 folder=out/('customer folder \u00e6\u00f8\u00e5 '+str(time.time_ns()));folder.mkdir(parents=True);exe=folder/'SAIV IT.exe';shutil.copyfile(R/M['output'],exe);assert list(folder.iterdir())==[exe]
 parent=PI();assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(folder),c.byref(si),c.byref(parent))
 end=time.monotonic()+20
 while time.monotonic()<end:
  ids=descendants(parent.pid)
  if ids:
   child=PI();child.pid=ids[0];child.process=k.OpenProcess(0x1fffff,False,child.pid);assert child.process;assert elevation(parent.process)==0 and elevation(child.process)==0,'Unexpected elevation';return child,(parent,folder)
  time.sleep(.1)
 diagnostics=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if pid.value==parent.pid:
   @CB
   def ch(ctrl,l):
    b=c.create_unicode_buffer(1000);u.GetWindowTextW(ctrl,b,1000);diagnostics.append(b.value);return True
   u.EnumChildWindows(h,ch,0)
  return True
 u.EnumDesktopWindows(desk,enum,0);k.TerminateProcess(parent.process,1);k.CloseHandle(parent.thread);k.CloseHandle(parent.process);raise AssertionError(diagnostics)
def finish(bundle):
 parent,folder=bundle
 assert k.WaitForSingleObject(parent.process,10000)==0
 code=w.DWORD();k.GetExitCodeProcess(parent.process,c.byref(code));k.CloseHandle(parent.thread);k.CloseHandle(parent.process)
 assert len(list(folder.iterdir()))==1,'Launcher wrote files beside customer EXE'
