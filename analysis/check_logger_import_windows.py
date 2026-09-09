"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test';out.mkdir(exist_ok=True)
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
pi=PI();exe=ROOT/'SAIV_Instrument_Terminal_v1.2.0_Sept2026.exe';assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(out),c.byref(si),c.byref(pi))
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
report=[]
try:
 main=waitfor('TForm1');time.sleep(2)
 command=next(i for t,i in menus(u.GetMenu(main)) if 'Import CSV/TXT' in t)
 for filename,oxygen in [('2026_09_03_20-28-52_C.txt',3),('2026_09_07_19-34-42_C.txt',3)]:
  assert u.PostMessageW(main,0x111,command,0)
  dialog=waitfor('#32770');cs=children(dialog);print('Importing',filename,flush=True)
  edit=next(h for h,t,cl,i in cs if cl=='Edit' and i in (1148,1152))
  settext(edit,ROOT/'data'/filename);click(dialog,1)
  wizard=waitfor('SITImportChoices');steps=[]
  for turn in range(25):
   if not any(h==wizard for h,t,cl in windows()):break
   title=text(u.GetDlgItem(wizard,101));steps.append(title);print(title,flush=True)
   if 'OxR' in title:u.SendMessageW(u.GetDlgItem(wizard,102),0x14e,oxygen,0);capture(wizard,out/('import_oxygen_'+filename+'.png'))
   if 'conditions' in title:
    if 'Surface' in filename or filename.startswith('2026_09_07'):
     settext(u.GetDlgItem(wizard,110),'10');settext(u.GetDlgItem(wizard,111),'35');settext(u.GetDlgItem(wizard,112),'1013.25')
    capture(wizard,out/('import_conditions_'+filename+'.png'))
   click(wizard,1)
  view=waitfor('SITImportData',filename);capture(view,out/('import_view_'+filename+'.png'))
  count=u.SendMessageW(u.GetDlgItem(view,210),0x1004,0,0);assert count==(79 if '09_03' in filename else 3),count
  export=out/('export_'+str(time.time_ns())+'_'+filename)
  click(view,201);save=waitfor('#32770','Export all fields')
  edit=next(h for h,t,cl,i in children(save) if cl=='Edit');settext(edit,export);click(save,1)
  msg=waitfor('#32770','SAIV IT');print('Export complete',filename,flush=True);u.PostMessageW(msg,0x111,2,0);time.sleep(.2)
  assert export.exists();report.append(dict(file=filename,rows=count,steps=steps,export=str(export)))
  u.PostMessageW(view,0x10,0,0);time.sleep(.3)
 # Cancel must leave the original data state and main window usable.
 u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770');edit=next(h for h,t,cl,i in children(dlg) if cl=='Edit' and i in (1148,1152));settext(edit,ROOT/'data/2026_09_03_20-28-52_C.txt');click(dlg,1);wiz=waitfor('SITImportChoices');click(wiz,2);assert not any(cl=='SITImportData' for h,t,cl in windows())
 # APB5 must still run through the unmodified native importer.
 u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770');edit=next(h for h,t,cl,i in children(dlg) if cl=='Edit' and i in (1148,1152));settext(edit,ROOT/'data/26090606_18.11.51.txt');click(dlg,1);time.sleep(2)
 def read32(addr):
  v=w.DWORD();assert k.ReadProcessMemory(pi.process,addr,c.byref(v),4,None);return v.value
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=read32(peb.value+8)
 count=read32(read32(base+0x1b16c0));print('APB5 native rows',count,'windows',windows(),flush=True);assert count==43,count
 report.append(dict(file='26090606_18.11.51.txt',native_rows=count,cancel_test=True))
 (out/'logger_import_gui_validation.json').write_text(json.dumps(report,indent=2));print('PASS',report,flush=True)
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)
