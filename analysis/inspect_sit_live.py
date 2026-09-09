"""Interactive inspection of an owned SIT instance; captures actual GUI state."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import sys, time, json
from check_startup_windows import k, u, n, SI, PI, CB
from capture_window import capture

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'analysis/runtime_test/sit_live_review'
OUT.mkdir(parents=True, exist_ok=True)
STATE = OUT / 'session.json'
u.OpenDesktopW.argtypes=[w.LPCWSTR,w.DWORD,w.BOOL,w.DWORD];u.OpenDesktopW.restype=w.HANDLE
u.GetMenu.argtypes=[w.HWND];u.GetMenu.restype=w.HMENU
u.GetSubMenu.argtypes=[w.HMENU,c.c_int];u.GetSubMenu.restype=w.HMENU
u.GetMenuItemCount.argtypes=[w.HMENU]
u.GetMenuItemID.argtypes=[w.HMENU,c.c_int];u.GetMenuItemID.restype=w.UINT
u.GetMenuStringW.argtypes=[w.HMENU,w.UINT,w.LPWSTR,c.c_int,w.UINT]
u.GetMenuState.argtypes=[w.HMENU,w.UINT,w.UINT]
u.GetDlgCtrlID.argtypes=[w.HWND]
u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)]
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
u.SetForegroundWindow.argtypes=[w.HWND]
k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE

def text(h, cls=False):
 b=c.create_unicode_buffer(8192);(u.GetClassNameW if cls else u.GetWindowTextW)(h,b,len(b));return b.value
def rect(h):
 r=w.RECT();u.GetWindowRect(h,c.byref(r));return [r.left,r.top,r.right,r.bottom]
def children(h):
 rows=[]
 @CB
 def enum(ch,l):
  rows.append(dict(hwnd=ch,text=text(ch),cls=text(ch,True),id=u.GetDlgCtrlID(ch),visible=bool(u.IsWindowVisible(ch)),rect=rect(ch)));return True
 u.EnumChildWindows(h,enum,0);return rows
def menus(h):
 rows=[]
 for i in range(max(0,u.GetMenuItemCount(h))):
  b=c.create_unicode_buffer(512);u.GetMenuStringW(h,i,b,len(b),0x400)
  sub=u.GetSubMenu(h,i)
  rows.append(dict(text=b.value,id=u.GetMenuItemID(h,i),state=u.GetMenuState(h,i,0x400),children=menus(sub) if sub else []))
 return rows

desk=u.OpenDesktopW('default',0,False,0x1ff)
assert desk,c.WinError(c.get_last_error())
action=sys.argv[1] if len(sys.argv)>1 else 'snapshot'
if action in ('walk','walkmenus'):
 import subprocess
 def run(*args):
  p=subprocess.run([sys.executable,__file__,*map(str,args)],capture_output=True,text=True,check=True)
  return json.loads(p.stdout)
 if action=='walk':
  for command in sys.argv[2:]:
   run('dismiss');result=run('command',command)
   (OUT/('visit_command_'+command+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
   print(json.dumps(dict(command=command,windows=[(r['title'],r['image']) for r in result['windows'] if r['cls'] not in ('TForm1','TApplication')])),flush=True)
 else:
  for label,root,keys in [('export','f',[40,39]),('tables','v',[40,39]),('time_graph','v',[40,40,39,39]),('depth_graph','v',[40,40,39,40,39])]:
   run('dismiss');run('menu',root);run('key',*keys);result=run('snapshot',label)
   (OUT/('visit_menu_'+label+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
   print(json.dumps(result),flush=True)
 run('dismiss');u.CloseDesktop(desk);sys.exit(0)
if action=='start':
 from single_exe_test_support_143 import start
 si=SI();si.cb=c.sizeof(si);si.desktop='winsta0\\default';si.flags=1;si.show=1
 pi,bundle=start(si,desk,OUT)
 STATE.write_text(json.dumps(dict(pid=pi.pid,parent_pid=bundle[0].pid,folder=str(bundle[1]))))
 k.CloseHandle(pi.process);k.CloseHandle(bundle[0].thread);k.CloseHandle(bundle[0].process)
 time.sleep(2)
state=json.loads(STATE.read_text())
proc=k.OpenProcess(0x410,False,state['pid']);assert proc,c.WinError(c.get_last_error())
def windows():
 rows=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if pid.value==state['pid'] and u.IsWindowVisible(h):rows.append(h)
  return True
 u.EnumDesktopWindows(desk,enum,0);return rows
def read32(a):
 value=w.DWORD();assert k.ReadProcessMemory(proc,a,c.byref(value),4,None);return value.value
def objects():
 peb=c.c_size_t();assert n.NtQueryInformationProcess(proc,26,c.byref(peb),c.sizeof(peb),None)==0
 base=read32(peb.value+8);form=read32(base+0x1c8964);fields=read32(read32(form)-56)
 def read(a,size):
  b=c.create_string_buffer(size);assert k.ReadProcessMemory(proc,a,b,size,None);return b.raw
 count=int.from_bytes(read(fields,2),'little');p=fields+6;result={}
 for _ in range(count):
  off=read32(p);length=read(p+6,1)[0];name=read(p+7,length).decode();obj=read32(form+off);p+=7+length
  result[name]=obj
 return result
hs=windows();main=next((h for h in hs if text(h,True)=='TForm1'),None)
if action=='open':
 path=Path(sys.argv[2]).resolve();assert path.is_file()
 u.PostMessageW(main,0x111,2,0);time.sleep(.35)
 dialog=next(h for h in windows() if text(h,True)=='#32770')
 edit=next(ch['hwnd'] for ch in children(dialog) if ch['cls']=='Edit')
 b=c.create_unicode_buffer(str(path));u.SendMessageW(edit,0xc,0,c.addressof(b));u.PostMessageW(dialog,0x111,1,0);time.sleep(.5)
 dialog=next(h for h in windows() if text(h,True)=='TSelectDlg')
 for ch in children(dialog):
  if 'Mask measurements' in ch['text']:u.SendMessageW(ch['hwnd'],0xf1,0,0)
 ok=next(ch['hwnd'] for ch in children(dialog) if ch['text'].replace('&','')=='OK')
 u.PostMessageW(ok,0xf5,0,0);time.sleep(.5)
elif action=='command':
 target=int(sys.argv[3]) if len(sys.argv)>3 else main
 u.PostMessageW(target,0x111,int(sys.argv[2],0),0);time.sleep(.7)
elif action=='close':
 u.PostMessageW(int(sys.argv[2]),0x10,0,0);time.sleep(.5)
elif action=='text':
 b=c.create_unicode_buffer(sys.argv[3]);u.SendMessageW(int(sys.argv[2]),0xc,0,c.addressof(b));time.sleep(.2)
elif action=='button':
 obj=objects()[sys.argv[2]];parent=read32(obj+0x24);hwnd=read32(parent+0x14c)
 x=read32(obj+0x30)+read32(obj+0x38)//2;y=read32(obj+0x34)+read32(obj+0x3c)//2
 u.PostMessageW(hwnd,0x201,1,x|(y<<16));u.PostMessageW(hwnd,0x202,0,x|(y<<16));time.sleep(.7)
elif action=='click':
 u.PostMessageW(int(sys.argv[2]),0xf5,0,0);time.sleep(.6)
elif action=='caption':
 matches=[ch['hwnd'] for h in windows() for ch in children(h) if ch['visible'] and ch['text']==sys.argv[2]]
 assert len(matches)==1,matches
 u.PostMessageW(matches[0],0xf5,0,0);time.sleep(.6)
elif action=='mouse':
 h=int(sys.argv[2]);xy=int(sys.argv[3])|(int(sys.argv[4])<<16)
 u.PostMessageW(h,0x201,1,xy);u.PostMessageW(h,0x202,0,xy);time.sleep(.5)
elif action=='menu':
 u.SetForegroundWindow(main);u.PostMessageW(main,0x112,0xf100,ord(sys.argv[2]));time.sleep(.5)
elif action=='key':
 for value in sys.argv[2:]:
  key=int(value,0);u.PostMessageW(main,0x100,key,0);u.PostMessageW(main,0x101,key,0);time.sleep(.25)
elif action=='dismiss':
 u.PostMessageW(main,0x1f,0,0)
 for h in windows():
  if text(h,True) not in ('TForm1','TApplication','#32768'):
   cancel=next((ch['hwnd'] for ch in children(h) if ch['visible'] and ch['text'].replace('&','').lower() in ('cancel','avbryt','close')),None)
   if cancel:u.PostMessageW(cancel,0xf5,0,0)
   else:u.PostMessageW(h,0x10,0,0)
 time.sleep(.3)
elif action=='objects':
 print(json.dumps(list(objects())))

label=(sys.argv[2] if action=='snapshot' and len(sys.argv)>2 else action)+'_'+str(time.time_ns())
report=dict(pid=state['pid'],windows=[],menus=menus(u.GetMenu(main)) if main else [])
for i,h in enumerate(windows()):
 row=dict(hwnd=h,title=text(h),cls=text(h,True),rect=rect(h),children=children(h))
 try:
  from PIL import ImageGrab
  if row['rect'][2]>row['rect'][0] and row['rect'][3]>row['rect'][1]:
   live_path=OUT/(label+'_'+str(i)+'_screen.png');ImageGrab.grab(bbox=tuple(row['rect'])).save(live_path);row['screen_image']=str(live_path)
 except Exception as e:row['screen_capture_error']=str(e)
 try:
  path=OUT/(label+'_'+str(i)+'.png');capture(h,path);row['image']=str(path)
 except Exception as e:row['capture_error']=str(e)
 report['windows'].append(row)
try:
 from PIL import ImageGrab
 ImageGrab.grab().save(OUT/(label+'_desktop.png'))
except Exception as e:report['desktop_error']=str(e)
(OUT/(label+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(OUT/(label+'.json')),windows=[dict(hwnd=r['hwnd'],title=r['title'],cls=r['cls'],image=r.get('image'),controls=[(ch['hwnd'],ch['text'],ch['cls']) for ch in r['children'] if ch['visible'] and (ch['text'] or ch['cls'] in ('Edit','TEdit'))]) for r in report['windows']]),indent=2))
k.CloseHandle(proc);u.CloseDesktop(desk)
