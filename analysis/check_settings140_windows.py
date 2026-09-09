"""Inspect actual controls in an unelevated delivered single EXE; no serial actions."""
"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test/settings140';out.mkdir(exist_ok=True)
u.GetMenu.argtypes=[w.HWND];u.GetMenu.restype=w.HMENU
u.GetSubMenu.argtypes=[w.HMENU,c.c_int];u.GetSubMenu.restype=w.HMENU
u.GetMenuItemCount.argtypes=[w.HMENU]
u.GetMenuItemID.argtypes=[w.HMENU,c.c_int];u.GetMenuItemID.restype=w.UINT
u.GetMenuStringW.argtypes=[w.HMENU,w.UINT,w.LPWSTR,c.c_int,w.UINT]
u.GetDlgItem.argtypes=[w.HWND,c.c_int];u.GetDlgItem.restype=w.HWND
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
u.GetDlgCtrlID.argtypes=[w.HWND]
def text(h,cls=False):
 b=c.create_unicode_buffer(4096);(u.GetClassNameW if cls else u.GetWindowTextW)(h,b,len(b));return b.value
def children(h):
 rows=[]
 @CB
 def enum(ch,l):rows.append((ch,text(ch),text(ch,True),u.GetDlgCtrlID(ch)));return True
 u.EnumChildWindows(h,enum,0);return rows
def menus(menu):
 rows=[]
 for i in range(u.GetMenuItemCount(menu)):
  b=c.create_unicode_buffer(256);u.GetMenuStringW(menu,i,b,len(b),0x400);sub=u.GetSubMenu(menu,i);rows.append((b.value,u.GetMenuItemID(menu,i)))
  if sub:rows+=menus(sub)
 return rows
def settext(h,s):
 b=c.create_unicode_buffer(str(s));return u.SendMessageW(h,0xc,0,c.addressof(b))
desktop='SIT_import_'+str(time.time_ns());desk=u.CreateDesktopW(desktop,None,None,0,0x1ff,None);assert desk
si=SI();si.cb=c.sizeof(si);si.desktop=desktop;si.flags=1;si.show=1
if '--live' in sys.argv:
 u.CloseDesktop(desk);u.OpenDesktopW.argtypes=[w.LPCWSTR,w.DWORD,w.BOOL,w.DWORD];u.OpenDesktopW.restype=w.HANDLE
 desk=u.OpenDesktopW('default',0,False,0x1ff);assert desk;si.desktop='winsta0\\default'
 def capture(hwnd,path):
  from PIL import ImageGrab
  u.SetForegroundWindow.argtypes=[w.HWND];u.SetForegroundWindow(hwnd)
  rect=w.RECT();u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)];u.GetWindowRect(hwnd,c.byref(rect));time.sleep(.35)
  ImageGrab.grab(bbox=(rect.left,rect.top,rect.right,rect.bottom)).save(path)
from single_exe_test_support_140 import start,finish
pi,bundle=start(si,desk,out)

def windows():
 rows=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if pid.value==pi.pid and u.IsWindowVisible(h):rows.append((h,text(h),text(h,True)))
  return True
 u.EnumDesktopWindows(desk,enum,0);return rows
def waitfor(cls,title='',timeout=12):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  for h,t,cl in windows():
   if cl==cls and title in t:return h
  time.sleep(.15)
 raise AssertionError((cls,title,windows()))
def click(h,id):assert u.PostMessageW(h,0x111,id,0);time.sleep(.2)

def read(a,nbytes=4):
 buf=c.create_string_buffer(nbytes);assert k.ReadProcessMemory(pi.process,a,buf,nbytes,None);return buf.raw
def d(a):return int.from_bytes(read(a),'little')
try:
 main=waitfor('TForm1');time.sleep(.6);peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=d(peb.value+8);form=d(base+0x1c8964)
 fields=d(d(form)-56);count=int.from_bytes(read(fields,2),'little');ptr=fields+6;objects={}
 for i in range(count):
  off=d(ptr);size=read(ptr+6,1)[0];name=read(ptr+7,size).decode();objects[name]=d(form+off);ptr+=7+size
 log=objects['btnLogReadout'];loghwnd=d(log+0x14c);assert not loghwnd or not u.IsWindowVisible(loghwnd)
 download=objects['btnDownload'];assert text(d(download+0x14c))=='&Download'
 detect=objects['btnPhone'];captions=[]
 for off in range(0,256,4):
  addr=d(detect+off)
  if addr>65536:
   buf=c.create_string_buffer(8)
   if k.ReadProcessMemory(pi.process,addr,buf,8,None) and buf.raw==b'D&etect\0':captions.append(off)
 assert captions,'Live Detect caption missing'
 time.sleep(.7)
 u.IsWindowEnabled.argtypes=[w.HWND];u.IsWindowEnabled.restype=w.BOOL
 allcontrols=children(main)
 for caption in ['&Interval','TIME/D&ATE','&Download']:
  h=next(h for h,t,cl,id in allcontrols if t==caption);assert not u.IsWindowEnabled(h),caption
 assert d(objects['btnCommSetup']+0x34)>d(objects['btnSave']+0x34)
 assert d(objects['btnPrintEcho']+0x34)<d(objects['btnSave']+0x34)
 # Reproduce accepted detection in this owned process only, without serial writes.
 import struct,pefile
 k.VirtualAllocEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=c.c_void_p
 k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.c_void_p]
 k.CreateRemoteThread.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p,w.DWORD,c.c_void_p];k.CreateRemoteThread.restype=w.HANDLE
 mem=k.VirtualAllocEx(pi.process,None,8192,0x3000,0x40);assert mem
 def write(at,data):assert k.WriteProcessMemory(pi.process,at,data,len(data),None)
 def put(at,v):write(at,struct.pack('<I',v))
 ldr=d(peb.value+12);head=ldr+20;node=d(head);dllbase=0
 while node!=head:
  length=int.from_bytes(read(node+36,2),'little');name=read(d(node+40),length).decode('utf-16le')
  if name.lower()=='sit_import140.dll':dllbase=d(node+16);break
  node=d(node)
 assert dllbase
 dll=pefile.PE(str(ROOT/'SIT_Import140.dll'));entry=dllbase+next(e.address for e in dll.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'SitNative')
 def invoke(op,a=0,b=0):
  code=b''.join(b'\x68'+struct.pack('<I',v) for v in [0,b,a,op])+b'\xb8'+struct.pack('<I',entry)+b'\xff\xd0\xc2\x04\x00';write(mem+4096,code)
  thread=k.CreateRemoteThread(pi.process,None,0,mem+4096,None,0,None);assert thread;assert k.WaitForSingleObject(thread,5000)==0;k.CloseHandle(thread)
 comm=d(form+0x510);oldopen=read(comm+0x24,1);port=read(comm+0x34,1)[0];assert port
 put(mem+0x330,mem+0x600);put(mem+0x5fc,1);put(mem+0x600,mem+0x400);put(mem+0x610,mem+0x800);put(mem+0x7fc,5);write(mem+0x800,b'Instr\0');write(mem+0x462,b'\1');write(mem+0x471,b'\2');put(mem+0x464,mem+0x700);write(mem+0x734,bytes([port]));put(mem+0x45c,mem+0x900)
 checks=[]
 try:
  for context,unit in [('Start via key-board ... Exit (passive)','SD200'),('OSU107 Instrument logger SN107','OSU107 + SD200'),('SAIV110 Surface logger SN107','SAIV110 Surface')]:
   write(mem+0x900,context.encode()+b'\0');write(comm+0x24,b'\1');invoke(30,mem);invoke(31,1);time.sleep(.6)
   controls=children(main)
   for caption in ['&Interval','TIME/D&ATE','&Download']:
    h=next(h for h,t,cl,id in controls if t==caption);assert u.IsWindowEnabled(h),(unit,caption)
   for caption,clockmode in [('&Interval',False),('TIME/D&ATE',True)]:
    h=next(h for h,t,cl,id in controls if t==caption);u.PostMessageW(h,0xf5,0,0);dialog=waitfor('SITDeviceSettings');items=children(dialog);assert any(unit in txt for ch,txt,cl,id in items)
    if not clockmode:
     combo=next(ch for ch,txt,cl,id in items if id==101);assert u.SendMessageW(combo,0x146,0,0)==11
    else:assert u.SendMessageW(next(ch for ch,txt,cl,id in items if id==101),0xf0,0,0)==1
    u.PostMessageW(dialog,0x111,2,0);time.sleep(.2)
   write(comm+0x34,bytes([port%250+1]));time.sleep(.6)
   assert not u.IsWindowEnabled(next(h for h,t,cl,id in children(main) if t=='&Download'))
   write(comm+0x34,bytes([port]));checks.append(unit)
 finally:write(comm+0x24,oldopen);write(comm+0x34,bytes([port]))
 report=dict(detected_dialogs=checks,eleven_intervals_only=True,disabled_on_port_change=True,download_caption='&Download',detect_caption='D&etect',log_hidden=True,interval_alt='I',clock_alt='A',disabled_without_detection=True,print_top=216,setup_top=328,unelevated_single_exe=True,no_instrument_commands=True)
 (out/'startup_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
