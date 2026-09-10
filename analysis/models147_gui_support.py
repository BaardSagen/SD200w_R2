"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test/models147gui';out.mkdir(exist_ok=True)
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
from single_exe_test_support_147 import start,finish,cache
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

def select(h,control_id,value):
 ctrl=u.GetDlgItem(h,control_id);u.SendMessageW(ctrl,0x14e,value,0);u.PostMessageW(h,0x111,control_id|(1<<16),ctrl);time.sleep(.12)
def dismiss(h):
 button=next(ch for ch,t,cl,id in children(h) if cl=='Button');u.PostMessageW(button,0xf5,0,0);time.sleep(.2)
# Test preferences use a unique registry key patched only in our owned DLL process memory.
import struct,pefile,uuid,winreg,csv,re,io
registry='Software\\MHP\\SIT_PresetTest_'+uuid.uuid4().hex[:5]
originalRegistry='Software\\MHP\\SdInstr\\ConvertPresetsV1'
assert len(registry)<=len(originalRegistry)
keyAccess=winreg.KEY_ALL_ACCESS|winreg.KEY_WOW64_32KEY
k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.c_void_p]
k.VirtualProtectEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,c.POINTER(w.DWORD)]
k.VirtualAllocEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=c.c_void_p
k.CreateRemoteThread.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p,w.DWORD,c.c_void_p];k.CreateRemoteThread.restype=w.HANDLE
k.GetExitCodeThread.argtypes=[w.HANDLE,c.POINTER(w.DWORD)]
def read(a,nbytes=4):
 buf=c.create_string_buffer(nbytes);assert k.ReadProcessMemory(pi.process,a,buf,nbytes,None);return buf.raw
def d(a):return int.from_bytes(read(a),'little')
def write(a,data):
 old=w.DWORD();assert k.VirtualProtectEx(pi.process,a,len(data),0x40,c.byref(old));assert k.WriteProcessMemory(pi.process,a,data,len(data),None);k.VirtualProtectEx(pi.process,a,len(data),old.value,c.byref(old))
def prepare():
 main=waitfor('TForm1');time.sleep(2);peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=d(peb.value+8)
 mem=k.VirtualAllocEx(pi.process,None,4096,0x3000,0x40);assert mem
 path=str(cache()/'SIT_Import147.dll').encode('mbcs')+b'\0';write(mem+128,path)
 code=b'\x6a\x08\x6a\x00\x68'+struct.pack('<I',mem+128)+b'\xb8'+struct.pack('<I',d(base+0x1c9214))+b'\xff\xd0\xc2\x04\x00';write(mem,code)
 thread=k.CreateRemoteThread(pi.process,None,0,mem,None,0,None);assert thread;assert k.WaitForSingleObject(thread,10000)==0;module=w.DWORD();assert k.GetExitCodeThread(thread,c.byref(module));k.CloseHandle(thread);assert module.value
 blob=(ROOT/'SIT_Import147.dll').read_bytes();dll=pefile.PE(data=blob);at=blob.index(originalRegistry.encode('utf-16le'));write(module.value+dll.get_rva_from_offset(at),(registry+'\0').encode('utf-16le'))
 return main
def saved():
 try:
  with winreg.OpenKey(winreg.HKEY_CURRENT_USER,registry,0,keyAccess) as key:
   result={};i=0
   while True:
    try:name,value,typ=winreg.EnumValue(key,i);result[name]=value;i+=1
    except OSError:break
   return result
 except FileNotFoundError:return {}
def openfile(main,path):
 button=next(h for h,t,cl,id in children(main) if t=='&Convert' and cl=='TButton');u.PostMessageW(button,0xf5,0,0);dlg=waitfor('#32770','Convert CSV/TXT');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),path);click(dlg,1)
def export(view,name):
 target=out/(name+'_'+str(time.time_ns())+'.txt');click(view,201);dlg=waitfor('#32770','Export all fields');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),target);click(dlg,1);dismiss(waitfor('#32770','SAIV IT'));u.PostMessageW(view,0x10,0,0);time.sleep(.2);return target
def table(p):
 lines=p.read_text(encoding='utf-8-sig').splitlines();idx=next(i for i,l in enumerate(lines) if l.startswith('FIELDS:'));return list(csv.DictReader([lines[idx][7:].strip()]+lines[idx+1:],delimiter=';'))
