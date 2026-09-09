"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test/import136';out.mkdir(exist_ok=True)
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
from single_exe_test_support_136 import start,finish
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

try:
 main=waitfor('TForm1');time.sleep(2);print(menus(u.GetMenu(main)),flush=True);command=next(i for t,i in menus(u.GetMenu(main)) if 'Import CSV/TXT' in t)
 u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770');edit=next(h for h,t,cl,i in children(dlg) if cl=='Edit' and i in (1148,1152));settext(edit,ROOT/'data/26090606_18.11.51.txt');click(dlg,1)
 save=waitfor('#32770','Lagre');print(children(save),flush=True)
 target=out/('native_optical_'+str(time.time_ns())+'.SD2');edit=next(h for h,t,cl,i in children(save) if cl=='Edit');settext(edit,target);click(save,1);time.sleep(2);print('windows',windows(),flush=True)
 produced=list(out.glob(target.stem+'.*'));print([(f.name,f.stat().st_size) for f in produced],flush=True)
 import struct,re
 rows=[dict(re.findall(r'([A-Z]+)([+-]?[0-9.]+)',line)) for line in (ROOT/'data/26090606_18.11.51.txt').read_text().splitlines() if line.startswith('N0')]
 sd=target.read_bytes();op=target.with_suffix('.OP2').read_bytes();ox=target.with_suffix('.OX2').read_bytes()
 assert len(rows)==43 and len(sd)==52+52*43 and len(op)==8*43 and len(ox)==4*43
 assert struct.unpack_from('<H',sd,2)[0]==1237
 for i,row in enumerate(rows):
  values=struct.unpack_from('<6BHI5d',sd,52+52*i)
  assert values[7]==int(row['N'])
  for a,key in [(8,'S'),(10,'T'),(11,'P')]:assert abs(values[a]-float(row[key]))<1e-8,(i,key,values[a])
  for actual,key in zip(struct.unpack_from('<2f',op,8*i),['OF','OT']):assert abs(actual-float(row[key]))<1e-4,(i,key)
 old=[str(p) for p in (ROOT/'analysis/reference/native_ascii_sample_old').glob('sample.*')]
 for name in old:
  f=Path(name);new=target.with_suffix(f.suffix);assert new.read_bytes()==f.read_bytes(),f.suffix
 print('PASS 43 rows, salinity/temperature/pressure/OF/OT and all four native files byte-identical to original importer',flush=True)
 (out/'native_optical_paths.json').write_text(json.dumps([str(f) for f in produced]))
 selection=waitfor('TSelectDlg');u.PostMessageW(selection,0x10,0,0);time.sleep(.3)
 command=next(i for t,i in menus(u.GetMenu(main)) if 'Convert CSV/TXT' in t)
 u.PostMessageW(main,0x111,command,0);dlg=waitfor('#32770','Convert CSV/TXT');settext(next(h for h,t,cl,i in children(dlg) if cl=='Edit'),ROOT/'data/26090606_18.11.51.txt');click(dlg,1)
 notice=waitfor('#32770','SAIV IT');assert any('File > Import CSV/TXT' in t for h,t,cl,i in children(notice));click(notice,1)
 print('PASS legacy Convert directs to separate Import without native fallback',flush=True)

finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
