"""Inspect only an owned Studio GUI instance. Mouse actions use client coordinates."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import subprocess,json,sys,time
from PIL import ImageGrab
from capture_window import capture
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'saiv-studio/test-results'/(sys.argv[sys.argv.index('--results')+1] if '--results' in sys.argv else 'v030');OUT.mkdir(parents=True,exist_ok=True)
STATE=OUT/'session.json'
u=c.WinDLL('user32');CB=c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.EnumWindows.argtypes=[CB,w.LPARAM];u.EnumChildWindows.argtypes=[w.HWND,CB,w.LPARAM]
u.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)];u.IsWindowVisible.argtypes=[w.HWND]
u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,c.c_int];u.GetClassNameW.argtypes=[w.HWND,w.LPWSTR,c.c_int]
u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)];u.ClientToScreen.argtypes=[w.HWND,c.POINTER(w.POINT)]
u.SetForegroundWindow.argtypes=[w.HWND];u.SetWindowPos.argtypes=[w.HWND,w.HWND,c.c_int,c.c_int,c.c_int,c.c_int,w.UINT]
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
u.SetProcessDPIAware()
u.OpenDesktopW.argtypes=[w.LPCWSTR,w.DWORD,w.BOOL,w.DWORD];u.OpenDesktopW.restype=w.HANDLE
u.EnumDesktopWindows.argtypes=[w.HANDLE,CB,w.LPARAM]
u.CreateDesktopW.argtypes=[w.LPCWSTR,c.c_void_p,c.c_void_p,w.DWORD,w.DWORD,c.c_void_p];u.CreateDesktopW.restype=w.HANDLE
u.SetThreadDesktop.argtypes=[w.HANDLE];u.GetForegroundWindow.restype=w.HWND
action=sys.argv[1]
desktop=('StudioTest'+str(time.time_ns()) if '--private' in sys.argv else 'default') if action=='start' else json.loads(STATE.read_text()).get('desktop','default')
desk=u.CreateDesktopW(desktop,None,None,0,0x1ff,None) if action=='start' and '--private' in sys.argv else u.OpenDesktopW(desktop,0,False,0x1ff);assert desk
assert u.SetThreadDesktop(desk)
if action=='start':
 executable=Path(sys.argv[sys.argv.index('--exe')+1]).resolve() if '--exe' in sys.argv else ROOT/'saiv-studio/build/SAIVStudio.exe'
 args=[str(executable)]
 if '--normal' not in sys.argv:args+=['--terminal-test',str(OUT/'wire.bin')]
 if '--demo' in sys.argv:args+=['--demo']
 if '--open' in sys.argv:args+=['--open',str(Path(sys.argv[sys.argv.index('--open')+1]).resolve())]
 from check_startup_windows import k,SI,PI
 si=SI();si.cb=c.sizeof(si);si.desktop='winsta0\\'+desktop;si.flags=1;si.show=1;pi=PI()
 cmd=c.create_unicode_buffer(subprocess.list2cmdline(args))
 assert k.CreateProcessW(args[0],cmd,None,None,False,0,None,str(OUT),c.byref(si),c.byref(pi)),c.WinError(c.get_last_error())
 STATE.write_text(json.dumps({'pid':pi.pid,'desktop':desktop}));k.CloseHandle(pi.thread);k.CloseHandle(pi.process);time.sleep(2)
pid=json.loads(STATE.read_text())['pid']
def text(h,cls=False):
 b=c.create_unicode_buffer(8192);(u.GetClassNameW if cls else u.GetWindowTextW)(h,b,len(b));return b.value
def bounds(h):
 r=w.RECT();u.GetWindowRect(h,c.byref(r));return [r.left,r.top,r.right,r.bottom]
def windows():
 result=[]
 @CB
 def visit(h,l):
  p=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(p))
  if p.value==pid and u.IsWindowVisible(h):result.append(h)
  return True
 u.EnumDesktopWindows(desk,visit,0);return result
def children(h):
 result=[]
 @CB
 def visit(ch,l):
  if u.IsWindowVisible(ch):result.append(dict(hwnd=ch,text=text(ch),cls=text(ch,True),rect=bounds(ch)))
  return True
 u.EnumChildWindows(h,visit,0);return result
main=next(h for h in windows() if text(h,True)=='SAIVInstrumentStudio')
def activate():
 k=c.WinDLL('kernel32');k.GetCurrentThreadId.restype=w.DWORD
 u.AttachThreadInput.argtypes=[w.DWORD,w.DWORD,w.BOOL]
 current=k.GetCurrentThreadId();foreground=u.GetForegroundWindow();other=u.GetWindowThreadProcessId(foreground,None) if foreground else 0
 attached=other and other!=current and u.AttachThreadInput(current,other,True)
 try:u.SetForegroundWindow(main)
 finally:
  if attached:u.AttachThreadInput(current,other,False)
 if u.GetForegroundWindow()!=main and desktop=='default':
  # Click only a verified point in our own title bar, then restore the cursor.
  u.WindowFromPoint.argtypes=[w.POINT];u.WindowFromPoint.restype=w.HWND
  u.GetCursorPos.argtypes=[c.POINTER(w.POINT)]
  previous=w.POINT();u.GetCursorPos(c.byref(previous));r=bounds(main);point=w.POINT((r[0]+r[2])//2,r[1]+15)
  u.SetWindowPos(main,w.HWND(-1),0,0,0,0,3)
  try:
   if u.WindowFromPoint(point)==main:
    u.SetCursorPos(point.x,point.y);u.mouse_event(2,0,0,0,0);u.mouse_event(4,0,0,0,0);time.sleep(.15)
  finally:u.SetCursorPos(previous.x,previous.y);u.SetWindowPos(main,w.HWND(-2),0,0,0,0,3)
if action=='click':
 x,y=map(int,sys.argv[2:4]);activate();position=x|(y<<16)
 for pointer_action in (2,1,0):u.SendMessageW(main,0x8000+17,pointer_action,position);time.sleep(.25)
 time.sleep(.5)
elif action=='chars':
 end=time.monotonic()+4
 while u.GetForegroundWindow()!=main and time.monotonic()<end:activate();time.sleep(.01)
 assert u.GetForegroundWindow()==main,'Owned Studio window is not foreground'
 time.sleep(.15)
 for ch in sys.argv[2]:u.SendMessageW(main,0x102,ord(ch),1)
 time.sleep(.5)
elif action=='caption':
 ch=next(ch for h in windows() for ch in children(h) if ch['text'].replace('&','')==sys.argv[2]);u.PostMessageW(ch['hwnd'],0xf5,0,0);time.sleep(.8)
elif action=='text':
 b=c.create_unicode_buffer(sys.argv[3]);u.SendMessageW(int(sys.argv[2]),0xc,0,c.addressof(b));time.sleep(.3)
elif action=='file':
 dialog=next(h for h in windows() if text(h,True)=='#32770')
 edit=next(ch['hwnd'] for ch in children(dialog) if ch['cls']=='Edit')
 b=c.create_unicode_buffer(str(Path(sys.argv[2]).resolve()));u.SendMessageW(edit,0xc,0,c.addressof(b));u.PostMessageW(dialog,0x111,1,0);time.sleep(1)
elif action=='combo':
 dialog=next(h for h in windows() if text(h,True)=='SITImportChoices')
 combo=next(ch['hwnd'] for ch in children(dialog) if ch['cls']=='ComboBox')
 u.SendMessageW(combo,0x14e,int(sys.argv[2]),0);u.PostMessageW(dialog,0x111,102|(1<<16),combo);time.sleep(.3)
elif action=='dialog_button':
 dialog=next(h for h in windows() if text(h,True)=='#32770');u.PostMessageW(dialog,0x111,int(sys.argv[2]),0);time.sleep(.5)
elif action=='resize':u.SetWindowPos(main,None,0,0,int(sys.argv[2]),int(sys.argv[3]),6);time.sleep(.6)
elif action=='close':u.PostMessageW(main,0x10,0,0);time.sleep(.6);print('Closed owned Studio instance');sys.exit(0)
label=sys.argv[2] if action=='snapshot' and len(sys.argv)>2 else action
result=[]
for i,h in enumerate(h for h in windows() if text(h,True) not in ('UAC_InputIndicatorOverlayWnd','UAC Input Indicator')):
 path=OUT/(label+'_'+str(i)+'.png');r=bounds(h);capture(h,path,2);result.append(dict(hwnd=h,text=text(h),cls=text(h,True),rect=r,image=str(path),children=children(h)))
(OUT/(label+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
