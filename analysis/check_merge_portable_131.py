from pathlib import Path
import time,zipfile
portable=Path(__file__).resolve().parent/'runtime_test/merge131'/('portable_'+str(time.time_ns()))
portable.mkdir()
with zipfile.ZipFile(Path(__file__).resolve().parent.parent/'SAIV_IT_v1.3.1_portable.zip') as z:z.extractall(portable)
"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test/merge131';out.mkdir(exist_ok=True)
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
pi=PI();exe=portable/'SAIV_Instrument_Terminal_v1.3.1_Sept2026.exe';assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(out),c.byref(si),c.byref(pi))
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

def select(h,control_id,value):
 ctrl=u.GetDlgItem(h,control_id);u.SendMessageW(ctrl,0x14e,value,0);u.PostMessageW(h,0x111,control_id|(1<<16),ctrl);time.sleep(.12)
def dismiss(h):
 button=next(ch for ch,t,cl,id in children(h) if cl=='Button');u.PostMessageW(button,0xf5,0,0);time.sleep(.2)
# Remote LVITEM buffers belong to this owned test process only.
import struct
k.VirtualAllocEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=c.c_void_p
k.VirtualFreeEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD]
k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)]
u.IsWindowEnabled.argtypes=[w.HWND]
remote=k.VirtualAllocEx(pi.process,None,4096,0x3000,4);assert remote

def memory(data):
 b=c.create_string_buffer(data);assert k.WriteProcessMemory(pi.process,remote,b,len(data),None)
def cell(lst,row,col=0):
 data=struct.pack('<9I',1,row,col,0,0,remote+128,512,0,0);memory(data)
 u.SendMessageW(lst,0x1073,row,remote)
 b=c.create_string_buffer(1024);assert k.ReadProcessMemory(pi.process,remote+128,b,1024,None)
 return b.raw.decode('utf-16le').split(chr(0),1)[0]
def check(lst,row,on=True):
 memory(struct.pack('<9I',8,row,0,(2 if on else 1)<<12,0xf000,0,0,0,0));u.SendMessageW(lst,0x102b,row,remote);time.sleep(.08)
def scan(h,tol):
 settext(u.GetDlgItem(h,305),str(tol));click(h,306)
 end=time.monotonic()+30
 while time.monotonic()<end:
  if u.IsWindowEnabled(u.GetDlgItem(h,306)):break
  time.sleep(.1)
 else:raise AssertionError('Scan timeout')
 status=text(u.GetDlgItem(h,311));assert 'matching files' in status,status
 return [cell(u.GetDlgItem(h,310),i) for i in range(u.SendMessageW(u.GetDlgItem(h,310),0x1004,0,0))]
try:
 main=waitfor('TForm1');time.sleep(1);button=next(h for h,t,cl,id in children(main) if t=='&Merge' and cl=='TButton');u.PostMessageW(button,0xf5,0,0);h=waitfor('SITMerge')
 settext(u.GetDlgItem(h,301),portable/'data/2026_09_03_20-28-52_C.txt');settext(u.GetDlgItem(h,303),portable/'data/saiv110');found=scan(h,.5);assert len(found)==6
 (out/'portable_validation.json').write_text(json.dumps(dict(package='SAIV_IT_v1.3.1_portable.zip',extracted_to=str(portable),native_merge_button_works=True,matching_files_at_half_second=len(found)),indent=2));print('PASS extracted portable EXE/DLL and test folder: 6 matching files')
finally:
 k.VirtualFreeEx(pi.process,remote,0,0x8000);k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)
