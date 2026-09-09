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


import struct,pefile
k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.c_void_p]
k.VirtualProtectEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,c.POINTER(w.DWORD)]
k.VirtualAllocEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=c.c_void_p
exe=Path(sys.argv[1]).resolve();si=SI();si.cb=c.sizeof(si);pi=PI()
assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(exe.parent),c.byref(si),c.byref(pi))
report=[]
def read(a,n=4):
 b=c.create_string_buffer(n);assert k.ReadProcessMemory(pi.process,a,b,n,None);return b.raw
def d(a):return int.from_bytes(read(a),"little")
def write(a,b):
 old=w.DWORD();assert k.VirtualProtectEx(pi.process,a,len(b),0x40,c.byref(old));assert k.WriteProcessMemory(pi.process,a,b,len(b),None)
def button(obj):u.PostMessageW(d(obj+0x14c),0xf5,0,0)
try:
 time.sleep(2)
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=d(peb.value+8)
 mem=k.VirtualAllocEx(pi.process,None,4096,0x3000,0x40);assert mem and mem<2**32
 # Record the caller and outer EBP only for a NULL ClosePort argument.
 code=b"\x85\xc0\x75\x16\x50\x8b\x44\x24\x04\xa3"+struct.pack('<I',mem+128)+b"\x89\xe8\xa3"+struct.pack('<I',mem+132)+b"\x58\x90\x90\x90\x90\xe9"
 # Conditional jump targets the final jump, whose offset is 26.
 assert len(code)==27
 code+=struct.pack('<i',base+0x292179-(mem+31));write(mem,code);write(base+0x7f9c4,b'\xe9'+struct.pack('<i',mem-(base+0x7f9c9)))
 form=d(base+0x1c8964)
 for step,port in enumerate((7,11,7,7)):
  obj=d(form+0x4ec);par=d(obj+0x24);x=d(obj+0x30)+d(obj+0x38)//2;y=d(obj+0x34)+d(obj+0x3c)//2
  u.PostMessageW(d(par+0x14c),0x201,1,x|(y<<16));u.PostMessageW(d(par+0x14c),0x202,0,x|(y<<16))
  deadline=time.time()+30;selected=False
  while time.time()<deadline:
   time.sleep(.5)
   caller=d(mem+128)
   if caller:
    bp=d(mem+132);report.append(dict(error_caller=hex(caller),ebp=hex(bp),stack=read(bp,64).hex()));raise RuntimeError('NULL ClosePort')
   detect=d(d(base+0x1b1e1c));arr=d(detect+0x330)
   if not arr or not u.IsWindowVisible(d(detect+0x14c)):continue
   for row in range(d(arr-4)):
    worker=d(arr+row*20);ptr=d(arr+row*20+4);name=read(ptr,d(ptr-4)).decode('latin1') if ptr else ''
    if name.lower()=='com'+str(port) and read(worker+0x71,1)==b'\x02':
     listing=d(detect+0x2e4);lh=d(d(listing+0x248)+0x14c);xy=20|((8+16*row)<<16)
     u.PostMessageW(lh,0x201,1,xy);u.PostMessageW(lh,0x202,0,xy);time.sleep(.2)
     accepted=k.GetTickCount()
     if step%2:button(d(detect+0x2d0))
     else:u.PostMessageW(lh,0x203,1,xy);u.PostMessageW(lh,0x202,0,xy)
     report.append(dict(selected=port,row=row,method='OK' if step%2 else 'double_click',accepted=accepted,identity=read(d(worker+0x5c),min(d(d(worker+0x5c)-4),2000)).decode('latin1')));selected=True;break
   if selected:break
  assert selected, f"Instrument not found: COM{port}"
  time.sleep(3)
  assert not u.IsWindowVisible(d(detect+0x14c)), 'Detect did not close'
  count=d(base+0x29f000);report.append(dict(tx=[struct.unpack('<IIII',read(base+0x29f004+i*16,16)) for i in range(count)],terminal_port=read(d(form+0x510)+0x34,1).hex(),terminal_handle=d(d(form+0x510)+0x2c),baud=d(d(form+0x510)+0x30),parity=read(d(form+0x510)+0x4c,3).hex(),g_state=read(base+0x29d000+int(json.loads(Path('analysis/sd200_selection_g_delayed_manifest.json').read_text())['symbols']['pending']),24).hex()))
  newtx=report[-1]['tx'];h=report[-1]['terminal_handle'];post=[x for x in newtx if x[0]>=accepted and x[1]==h]
  assert [x[2] for x in post]==([71] if port==7 else []),(port,post)
  if port==7:assert post[0][0]-accepted>=1100 and post[0][3]==257
  report[-1]['verified_selection_tx']=post
  if not selected:report.append(dict(not_found=port));break
except Exception as e:report.append(dict(exception=str(e)))
finally:
 Path('analysis/select_delayed_physical_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));k.TerminateProcess(pi.process,0);k.CloseHandle(pi.thread);k.CloseHandle(pi.process)

if any("exception" in x for x in report):sys.exit(1)
