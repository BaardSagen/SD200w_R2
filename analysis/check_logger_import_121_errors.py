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

checks=[]
try:
 main=waitfor('TForm1');time.sleep(2);command=next(i for t,i in menus(u.GetMenu(main)) if 'Import CSV/TXT' in t)
 u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770');edit=next(h for h,t,cl,id in children(dlg) if cl=='Edit' and id in (1148,1152));settext(edit,ROOT/'data/2026_09_03_20-28-52_C.txt');click(dlg,1);wiz=waitfor('SITImportChoices')
 click(wiz,1);click(wiz,1);assert 'P - Pressure' in text(u.GetDlgItem(wiz,101));select(wiz,102,1);u.SendMessageW(u.GetDlgItem(wiz,121),0xf1,1,0);u.PostMessageW(wiz,0x111,121,0);time.sleep(.1)
 for lat,lon in [('91','5'),('60','181')]:
  settext(u.GetDlgItem(wiz,122),lat+', '+lon);click(wiz,1);msg=waitfor('#32770','SAIV IT');assert any('Latitude must be -90 to 90' in t for h,t,cl,id in children(msg));dismiss(msg);assert 'P - Pressure' in text(u.GetDlgItem(wiz,101));checks.append('reject GPS '+lat+','+lon)
 settext(u.GetDlgItem(wiz,122),'60, 5');click(wiz,1);click(wiz,1);assert 'Par - ' in text(u.GetDlgItem(wiz,101));select(wiz,102,1);click(wiz,1);msg=waitfor('#32770','SAIV IT');assert any('Select the area unit' in t for h,t,cl,id in children(msg));dismiss(msg);assert 'Par - ' in text(u.GetDlgItem(wiz,101));checks.append('reject unspecified PAR area unit')
 click(wiz,2);assert not any(cl in ('SITImportData','SITImportChoices') for h,t,cl in windows());u.IsWindowEnabled.argtypes=[w.HWND];assert u.IsWindowEnabled(main);checks.append('cancel after input errors restores main window')
 (out/'input_validation.json').write_text(json.dumps(dict(passed=checks),indent=2));print('PASS',len(checks),'input validation / cancellation checks')
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)
