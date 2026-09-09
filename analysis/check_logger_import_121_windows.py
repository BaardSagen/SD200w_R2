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
report=[]
try:
 main=waitfor('TForm1');time.sleep(2);command=next(i for t,i in menus(u.GetMenu(main)) if 'Import CSV/TXT' in t)
 synthetic=out/'synthetic_all_sensors.csv'
 synthetic.write_text('OSU107 Full DATE=2026-09-08 TIME=12:00:00\nCTDOXOFOT Par OxR Ser No 1240 AP1013.25\nFIELDS: COUNT;C;T;P;OF;OT;Par;OX;OxR;DATE;TIME\n1;42.914;10;0;0.38;1.20;0.0123;100;100;2026-09-08;12:00:00\n2;42.914;10;1000;0.38;1.20;0.0123;100;100;2026-09-08;12:00:02\n3;42.914;10;4000;0.38;1.20;0.0123;100;100;2026-09-08;12:00:04\n')
 cases=[(ROOT/'data/2026_09_03_20-28-52_C.txt',79,False),(ROOT/'data/2026_09_07_19-34-42_C.txt',3,False),(synthetic,3,True)]
 for path,expected,exclude in cases:
  u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770');edit=next(h for h,t,cl,id in children(dlg) if cl=='Edit' and id in (1148,1152));settext(edit,path);click(dlg,1);wiz=waitfor('SITImportChoices');steps=[];default_checks=[];saw_conditions=False
  for step in range(25):
   if not any(h==wiz for h,t,cl in windows()):break
   title=text(u.GetDlgItem(wiz,101));steps.append(title);print(path.name,title,flush=True)
   if 'conditions' in title:
    saw_conditions=True
    for id,value in [(110,'10'),(111,'35'),(112,'1013.25')]:
     ctrl=u.GetDlgItem(wiz,id)
     if ctrl:settext(ctrl,value)
    capture(wiz,out/(path.stem+'_conditions.png'))
   else:
    field=title.split(': ',1)[1].split(' -',1)[0];keep=u.GetDlgItem(wiz,120);assert keep;assert u.SendMessageW(keep,0xf0,0,0)==1;default_checks.append(field)
    if field=='C':select(wiz,102,1)
    if field=='P':
     select(wiz,102,1);u.SendMessageW(u.GetDlgItem(wiz,121),0xf1,1,0);u.PostMessageW(wiz,0x111,121,0);time.sleep(.1);settext(u.GetDlgItem(wiz,122),'60.3936119227684, 5.29588169849683');assert not u.GetDlgItem(wiz,123);assert text(u.GetDlgItem(wiz,128))=="Paste";assert u.GetDlgItem(wiz,129)
    if field=='Par':select(wiz,102,1);select(wiz,124,2 if exclude else 1)
    if field in ('OX','OxR'):select(wiz,102,3)
    if exclude and field in ('C','P','Par','OX','OxR'):u.SendMessageW(keep,0xf1,0,0)
    capture(wiz,out/(path.stem+'_'+field+'.png'))
   click(wiz,1)
  assert saw_conditions==('09_07' in path.name),(path,steps)
  view=waitfor('SITImportData',path.name);assert u.SendMessageW(u.GetDlgItem(view,210),0x1004,0,0)==expected
  capture(view,out/(path.stem+'_view.png'))
  target=out/(path.stem+'_export_'+str(time.time_ns())+'.txt');click(view,201);save=waitfor('#32770','Export all fields');edit=next(h for h,t,cl,id in children(save) if cl=='Edit');settext(edit,target);click(save,1);msg=waitfor('#32770','SAIV IT');dismiss(msg);assert target.exists()
  report.append(dict(file=str(path),export=str(target),rows=expected,exclude=exclude,original_checkboxes_default_on=default_checks,conditions_shown=saw_conditions,steps=steps));u.PostMessageW(view,0x10,0,0);time.sleep(.25)
 (out/'gui_validation.json').write_text(json.dumps(report,indent=2));print('PASS 1.2.1 GUI: names, C/S, depth/GPS, PAR source units, both oxygen sensors, retain/exclude and missing-only conditions',flush=True)
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)
