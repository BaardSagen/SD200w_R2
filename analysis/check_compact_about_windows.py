"""Inspect About and Disclaimer in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture as print_capture

def capture(hwnd,path):
 if '--live' not in sys.argv:
  return print_capture(hwnd,path)
 from PIL import ImageGrab
 u.SetForegroundWindow.argtypes=[w.HWND]
 u.SetForegroundWindow(hwnd)
 u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)]
 rect=w.RECT();assert u.GetWindowRect(hwnd,c.byref(rect))
 time.sleep(.5)
 ImageGrab.grab(bbox=(rect.left,rect.top,rect.right,rect.bottom)).save(path)

from build_compact_about import OUTPUT,DISCLAIMER
u.GetMenu.argtypes=[w.HWND];u.GetMenu.restype=w.HMENU
u.GetSubMenu.argtypes=[w.HMENU,c.c_int];u.GetSubMenu.restype=w.HMENU
u.GetMenuItemCount.argtypes=[w.HMENU]
u.GetMenuItemID.argtypes=[w.HMENU,c.c_int];u.GetMenuItemID.restype=w.UINT
u.GetMenuStringW.argtypes=[w.HMENU,w.UINT,w.LPWSTR,c.c_int,w.UINT]
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
out=Path(__file__).resolve().parent/'runtime_test';out.mkdir(exist_ok=True)
desktop='SD200W_credits_'+str(time.time_ns());desk=u.CreateDesktopW(desktop,None,None,0,0x1ff,None);assert desk
si=SI();si.cb=c.sizeof(si);si.desktop=desktop;si.flags=1;si.show=0
if '--live' in sys.argv:
 u.CloseDesktop(desk)
 u.OpenDesktopW.argtypes=[w.LPCWSTR,w.DWORD,w.BOOL,w.DWORD];u.OpenDesktopW.restype=w.HANDLE
 desk=u.OpenDesktopW('default',0,False,0x1ff);assert desk
 si.desktop='winsta0\\default';si.show=1
pi=PI();assert k.CreateProcessW(str(OUTPUT),None,None,None,False,0,None,str(out),c.byref(si),c.byref(pi))
def text(h,cls=False):
 b=c.create_unicode_buffer(4096);(u.GetClassNameW if cls else u.GetWindowTextW)(h,b,len(b));return b.value
def windows():
 rows=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if pid.value==pi.pid:rows.append((h,text(h),text(h,True),bool(u.IsWindowVisible(h))))
  return True
 u.EnumDesktopWindows(desk,enum,0);return rows
def children(h):
 rows=[]
 @CB
 def enum(ch,l):rows.append((ch,text(ch),text(ch,True)));return True
 u.EnumChildWindows(h,enum,0);return rows
def menus(menu):
 rows=[]
 for i in range(u.GetMenuItemCount(menu)):
  b=c.create_unicode_buffer(256);u.GetMenuStringW(menu,i,b,len(b),0x400)
  sub=u.GetSubMenu(menu,i)
  rows.append((b.value,u.GetMenuItemID(menu,i)))
  if sub:rows+=menus(sub)
 return rows
try:
 time.sleep(3)
 rows=windows();main=next(h for h,t,cl,v in rows if cl=='TForm1')
 menu=menus(u.GetMenu(main));print('About menu located',flush=True)
 command=next(i for t,i in menu if 'about' in t.lower())
 assert u.PostMessageW(main,0x111,command,0)
 time.sleep(1)
 rows=windows();print('About opened',flush=True)
 about=next(h for h,t,cl,v in rows if cl=='TAboutBoxNav' and v)
 u.RedrawWindow.argtypes=[w.HWND,c.c_void_p,w.HANDLE,w.UINT]
 u.RedrawWindow(about,None,None,0x185)
 time.sleep(1)
 print('About controls',[(t,cl,bool(u.IsWindowVisible(h))) for h,t,cl in children(about)],flush=True)
 capture(about,out/'about_v1_0_3.png')
 for h,t,cl in children(about):
  if cl=='TPanel':capture(h,out/'about_v1_0_3_panel.png')
 button=next(h for h,t,cl in children(about) if t=='Disclaimer')
 assert u.PostMessageW(button,0xf5,0,0)
 time.sleep(1)
 rows=windows();print('visible windows',[(t,cl) for h,t,cl,v in rows if v],flush=True)
 dialogs=[(h,children(h)) for h,t,cl,v in rows if v and h!=about and h!=main]
 print('dialogs',dialogs,flush=True)
 dialog=next((h,cs) for h,cs in dialogs if any(t.replace('&','').lower()=='ok' for ch,t,cl in cs))
 # Delphi labels are graphic controls, not child HWNDs. Read the live string
 # selected by the disclaimer handler, then visually inspect its screenshot.
 def read(address,size):
  buf=c.create_string_buffer(size);done=c.c_size_t()
  assert k.ReadProcessMemory(pi.process,address,buf,size,c.byref(done)) and done.value==size
  return buf.raw
 import struct
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0
 base=struct.unpack('<I',read(peb.value+8,4))[0]
 pointer=struct.unpack('<I',read(base+0x109e50,4))[0]
 size=struct.unpack('<I',read(pointer-4,4))[0]
 assert read(pointer,size).decode('ascii')==DISCLAIMER
 capture(dialog[0],out/'disclaimer_v1_0_3.png')
 ok=next(h for h,t,cl in dialog[1] if t.replace('&','').lower()=='ok')
 u.PostMessageW(ok,0xf5,0,0);time.sleep(.3)
 ok=next(h for h,t,cl in children(about) if t.replace('&','').lower()=='ok')
 u.PostMessageW(ok,0xf5,0,0);time.sleep(.3)
 assert not u.IsWindowVisible(about)
 (out/'credits_v1_0_3_validation.json').write_text(json.dumps(dict(exe=OUTPUT.name,about_opened=True,disclaimer_exact=True,dialogs_closed=True,screenshots=['about_v1_0_3.png','disclaimer_v1_0_3.png']),indent=2))
 print('PASS About and exact Disclaimer opened and closed')
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,3000);k.CloseHandle(pi.thread);k.CloseHandle(pi.process);u.CloseDesktop(desk)
