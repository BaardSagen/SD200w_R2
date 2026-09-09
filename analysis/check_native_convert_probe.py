"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=sorted((ROOT/'analysis/runtime_test/native_convert').glob('[0-9]*'))[-1]
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

import pefile,struct
source=ROOT/'analysis/single135/SAIV_IT_Runtime.exe';raw=bytearray(source.read_bytes());pe=pefile.PE(data=raw)
# This owned test runtime cannot open a serial port. No instrument traffic.
off=pe.get_offset_from_rva(0x7e8f8);raw[off:off+3]=b'\x31\xc0\xc3'
exe=out/'NATIVE_CONVERT_PROBE_ONLY.exe';exe.write_bytes(raw)
pi=PI();assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(out),c.byref(si),c.byref(pi))
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
  time.sleep(.1)
 raise AssertionError((cls,title,windows()))
def read(addr,size):
 b=c.create_string_buffer(size);assert k.ReadProcessMemory(pi.process,addr,b,size,None);return b.raw
def read32(addr):return struct.unpack('<I',read(addr,4))[0]
def printwindow(h,path):
 from capture_window import capture as cap
 cap(h,path)
try:
 main=waitfor('TForm1');time.sleep(1)
 # Close only the terminal window created by this owned process.
 for h,t,cl in windows():
  if cl=='TDlgInstr':u.PostMessageW(h,0x10,0,0)
 time.sleep(.3)
 ms=menus(u.GetMenu(main));print(ms[:28],flush=True)
 cmd=next(i for t,i in ms if t.replace('&','').startswith('Open'))
 u.PostMessageW(main,0x111,cmd,0);dlg=waitfor('#32770')
 edit=next(h for h,t,cl,i in children(dlg) if cl=='Edit' and i in (1148,1152))
 settext(edit,out/'convert_probe.SD2');u.PostMessageW(dlg,0x111,1,0);time.sleep(2)
 
 for h,t,cl in windows():
  if cl=='TSelectDlg':
   print('Range controls',children(h),flush=True)
   for ch,txt,typ,id in children(h):
    if typ=='TCheckBox' and 'Mask measurements' in txt: u.SendMessageW(ch,0xf1,0,0)
   button=next(ch for ch,txt,typ,id in children(h) if typ in ('TButton','TBitBtn') and txt.replace('&','').lower()=='ok')
   u.PostMessageW(button,0xf5,0,0);time.sleep(1)
 print('Opened windows',windows(),flush=True)
 for h,t,cl in windows():
  if cl=='#32770':print('Dialog',children(h),flush=True)
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=read32(peb.value+8)
 count=read32(read32(base+0x1b16c0));expected=json.loads((out/'projection.json').read_text())
 assert count==expected['rows'],(count,expected['rows'])
 table=read32(base+0x1b2150);data=read32(table)
 loaded=[list(struct.unpack('<5d',read(data+52*i+12,40))) for i in range(count)]
 assert loaded==expected['native_expected'],(loaded[:1],expected['native_expected'][:1])
 printwindow(main,out/'native_list.png')
 graph=next(i for t,i in ms if 'Salinity / Temperature' in t)
 u.PostMessageW(main,0x111,graph,0);time.sleep(1)
 printwindow(main,out/'native_graph.png')
 report=dict(native_rows=count,native_values_checked=count*5,all_native_values_exact=True,graph_command=graph,windows=windows(),physical_serial_disabled=True)
 (out/'gui_validation.json').write_text(json.dumps(report,indent=2))
 print('PASS',report,flush=True)
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)
