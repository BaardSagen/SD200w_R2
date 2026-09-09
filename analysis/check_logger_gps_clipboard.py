"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test/import121';out.mkdir(exist_ok=True)
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

u.GetProcessWindowStation.restype=w.HANDLE
u.CreateWindowStationW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p];u.CreateWindowStationW.restype=w.HANDLE
u.SetProcessWindowStation.argtypes=[w.HANDLE];u.CloseWindowStation.argtypes=[w.HANDLE]
original_station=u.GetProcessWindowStation();station_name='SITClipboard_'+str(time.time_ns());station=u.CreateWindowStationW(station_name,0,0x37f,None);
if not station:
 (out/'clipboard_validation.json').write_text(json.dumps(dict(status='SKIPPED',reason='Windows denied creation of an isolated window station',user_clipboard_untouched=True),indent=2));print('SKIP isolated clipboard test: Windows access denied; user clipboard untouched');sys.exit(0)
assert u.SetProcessWindowStation(station)

desktop='SIT_import_'+str(time.time_ns());desk=u.CreateDesktopW(desktop,None,None,0,0x1ff,None);assert desk
si=SI();si.cb=c.sizeof(si);si.desktop=station_name+chr(92)+desktop;si.flags=1;si.show=1
if '--live' in sys.argv:
 u.CloseDesktop(desk);u.OpenDesktopW.argtypes=[w.LPCWSTR,w.DWORD,w.BOOL,w.DWORD];u.OpenDesktopW.restype=w.HANDLE
 desk=u.OpenDesktopW('default',0,False,0x1ff);assert desk;si.desktop='winsta0\\default'
 def capture(hwnd,path):
  from PIL import ImageGrab
  u.SetForegroundWindow.argtypes=[w.HWND];u.SetForegroundWindow(hwnd)
  rect=w.RECT();u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)];u.GetWindowRect(hwnd,c.byref(rect));time.sleep(.35)
  ImageGrab.grab(bbox=(rect.left,rect.top,rect.right,rect.bottom)).save(path)
pi=PI();exe=ROOT/'SAIV_Instrument_Terminal_v1.2.1_Sept2026.exe';assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(out),c.byref(si),c.byref(pi))
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

try:
 main=waitfor('TForm1');time.sleep(2);command=next(i for t,i in menus(u.GetMenu(main)) if 'Import CSV/TXT' in t)
 u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770');edit=next(h for h,t,cl,id in children(dlg) if cl=='Edit' and id in (1148,1152));settext(edit,ROOT/'data/2026_09_03_20-28-52_C.txt');click(dlg,1);wiz=waitfor('SITImportChoices');click(wiz,1);click(wiz,1);select(wiz,102,1);u.SendMessageW(u.GetDlgItem(wiz,121),0xf1,1,0);u.PostMessageW(wiz,0x111,121,0);time.sleep(.2)
 gps=u.GetDlgItem(wiz,122);assert gps and not u.GetDlgItem(wiz,123);assert u.GetDlgItem(wiz,128) and u.GetDlgItem(wiz,129)
 u.OpenClipboard.argtypes=[w.HWND];u.EmptyClipboard.argtypes=[];u.SetClipboardData.argtypes=[w.UINT,w.HANDLE];u.SetClipboardData.restype=w.HANDLE
 k.GlobalAlloc.argtypes=[w.UINT,c.c_size_t];k.GlobalAlloc.restype=w.HANDLE;k.GlobalLock.argtypes=[w.HANDLE];k.GlobalLock.restype=c.c_void_p;k.GlobalUnlock.argtypes=[w.HANDLE]
 coordinate='60.3936119227684, 5.29588169849683';value=c.create_unicode_buffer(coordinate);memory=k.GlobalAlloc(2,c.sizeof(value));assert memory;ptr=k.GlobalLock(memory);assert ptr;c.memmove(ptr,value,c.sizeof(value));k.GlobalUnlock(memory)
 assert u.OpenClipboard(None);assert u.EmptyClipboard();assert u.SetClipboardData(13,memory);u.CloseClipboard()
 settext(gps,'1, 2');click(wiz,128);assert text(gps)==coordinate,text(gps);click(wiz,1);assert 'OF - Fluorescence' in text(u.GetDlgItem(wiz,101));click(wiz,2)
 result=dict(paste_replaces_entire_coordinate=True,single_field=True,google_maps_control_class=text(u.GetDlgItem(wiz,129),True) if u.GetDlgItem(wiz,129) else 'checked before closing',user_clipboard_untouched=True,isolated_window_station=station_name)
 (out/'clipboard_validation.json').write_text(json.dumps(result,indent=2));print('PASS Paste replaces GPS pair; validated without touching user clipboard')
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk);u.SetProcessWindowStation(original_station);u.CloseWindowStation(station)
