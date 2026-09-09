"""Exercise real GUI import in an owned process on a private desktop."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,sys
from check_startup_windows import k,u,n,SI,PI,CB
from capture_window import capture
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'analysis/runtime_test/presets134';out.mkdir(exist_ok=True)
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
from single_exe_test_support_134 import start,finish,cache
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
 path=str(cache()/'SIT_Import134.dll').encode('mbcs')+b'\0';write(mem+128,path)
 code=b'\x6a\x08\x6a\x00\x68'+struct.pack('<I',mem+128)+b'\xb8'+struct.pack('<I',d(base+0x1c9214))+b'\xff\xd0\xc2\x04\x00';write(mem,code)
 thread=k.CreateRemoteThread(pi.process,None,0,mem,None,0,None);assert thread;assert k.WaitForSingleObject(thread,10000)==0;module=w.DWORD();assert k.GetExitCodeThread(thread,c.byref(module));k.CloseHandle(thread);assert module.value
 blob=(ROOT/'SIT_Import134.dll').read_bytes();dll=pefile.PE(data=blob);at=blob.index(originalRegistry.encode('utf-16le'));write(module.value+dll.get_rva_from_offset(at),(registry+'\0').encode('utf-16le'))
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
 button=next(h for h,t,cl,id in children(main) if t=='&Convert' and cl=='TButton');u.PostMessageW(button,0xf5,0,0);dlg=waitfor('#32770','Convert TXT/CSV');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),path);click(dlg,1)
def export(view,name):
 target=out/(name+'_'+str(time.time_ns())+'.txt');click(view,201);dlg=waitfor('#32770','Export all fields');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),target);click(dlg,1);dismiss(waitfor('#32770','SAIV IT'));u.PostMessageW(view,0x10,0,0);time.sleep(.2);return target
def table(p):
 lines=p.read_text(encoding='utf-8-sig').splitlines();idx=next(i for i,l in enumerate(lines) if l.startswith('FIELDS:'));return list(csv.DictReader([lines[idx][7:].strip()]+lines[idx+1:],delimiter=';'))
report={}
try:
 main=prepare();assert not saved()
 raw=(ROOT/'data/2026_09_03_20-28-52_C.txt').read_text();a=out/'first_OSU.txt';a.write_text(raw)
 b=out/'another_day.csv';b.write_text(raw.replace('2026-09-03','2026-09-04').replace('AP1006.175','AP900'))
 openfile(main,a);wiz=waitfor('SITImportChoices');steps=[]
 for step in range(20):
  if not any(h==wiz for h,t,cl in windows()):break
  title=text(u.GetDlgItem(wiz,101));steps.append(title);field=title.split(': ',1)[1].split(' -',1)[0]
  if field in ('C','P','Par'):select(wiz,102,1)
  if field=='Par':select(wiz,124,2)
  if field=='OxR':select(wiz,102,3)
  if field in ('C','Par','OxR','OF'):u.SendMessageW(u.GetDlgItem(wiz,120),0xf1,0,0)
  if field=='T':u.SendMessageW(u.GetDlgItem(wiz,130),0xf1,0,0)
  click(wiz,1)
 view=waitfor('SITImportData');first=export(view,'first');initial=saved();assert len(initial)==1;report['first_fields']=steps
 # Terminate only our child and restart the delivered one-EXE file, keeping the isolated history.
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);pi,bundle=start(si,desk,out);main=prepare()
 openfile(main,b);prompt=waitfor('#32770','Previous conversion');promptText=' '.join(t for h,t,cl,id in children(prompt));assert 'first_OSU.txt' in promptText and re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',promptText);click(prompt,6)
 view=waitfor('SITImportData');assert not any(cl=='SITImportChoices' for h,t,cl in windows());second=export(view,'reused');aa,bb=table(first),table(second);assert len(aa)==len(bb)==79
 for x,y in zip(aa,bb):
  assert set(x)==set(y)
  for field in x:
   if field not in ('DATE','OxR_mg_L','OxR_mL_L'):assert x[field]==y[field],field
  assert x['DATE']!=y['DATE'];assert x['OxR_mg_L']!=y['OxR_mg_L']
 assert not {'C','Par','OxR','OF','Sound_velocity_SIT_m_s'}&set(aa[0]);assert {'S','Depth_m','Par_umol_m2_s','OxR_mg_L','OxR_mL_L'}<=set(aa[0]);assert 'Air pressure hPa=900' in second.read_text(encoding='utf-8-sig');report['reused_after_restart']=True;report['current_air_pressure_used']=True
 before=saved();openfile(main,b);prompt=waitfor('#32770','Previous conversion');click(prompt,7);wiz=waitfor('SITImportChoices')
 assert u.SendMessageW(u.GetDlgItem(wiz,102),0x147,0,0)==0;assert u.SendMessageW(u.GetDlgItem(wiz,120),0xf0,0,0)==1;click(wiz,2);assert saved()==before;report['no_opens_normal_wizard_cancel_preserves_history']=True
 openfile(main,b);prompt=waitfor('#32770','Previous conversion');click(prompt,2);assert saved()==before;report['cancel_prompt_preserves_history']=True
 changed=out/'different_layout.txt';lines=raw.splitlines();changed.write_text('\n'.join(l+';42' if l and l[0].isdigit() else l+';Extra' if l.startswith('FIELDS:') else l for l in lines));openfile(main,changed);wiz=waitfor('SITImportChoices');click(wiz,2);assert saved()==before;report['different_layout_does_not_reuse']=True
 # Save a GPS-enabled choice set, then verify only its position page needs review on reuse.
 openfile(main,a);prompt=waitfor('#32770','Previous conversion');click(prompt,7);wiz=waitfor('SITImportChoices')
 for step in range(20):
  if not any(h==wiz for h,t,cl in windows()):break
  title=text(u.GetDlgItem(wiz,101));field=title.split(': ',1)[1].split(' -',1)[0]
  if field=='P':
   select(wiz,102,1);u.SendMessageW(u.GetDlgItem(wiz,121),0xf1,1,0);u.PostMessageW(wiz,0x111,121,0);settext(u.GetDlgItem(wiz,122),'60.4, 5.3')
  click(wiz,1)
 export(waitfor('SITImportData'),'gps_first')
 openfile(main,b);prompt=waitfor('#32770','Previous conversion');click(prompt,6);wiz=waitfor('SITImportChoices');assert 'P - Pressure' in text(u.GetDlgItem(wiz,101));assert text(u.GetDlgItem(wiz,122))=='';assert u.SendMessageW(u.GetDlgItem(wiz,121),0xf0,0,0)==1
 settext(u.GetDlgItem(wiz,122),'59, 4');click(wiz,1);gps=export(waitfor('SITImportData'),'gps_new');assert '# GPS position: 59, 4;' in gps.read_text(encoding='utf-8-sig');report['gps_is_requested_again']=True
 # Calculation failure must not replace a successful record.
 before=saved();bad=out/'missing_pressure.txt';lines=raw.splitlines()
 for idx,line in enumerate(lines):
  if line and line[0].isdigit():
   cells=line.split(';');cells[3]='';lines[idx]=';'.join(cells);break
 bad.write_text('\n'.join(lines));openfile(main,bad);prompt=waitfor('#32770','Previous conversion');click(prompt,6);wiz=waitfor('SITImportChoices');settext(u.GetDlgItem(wiz,122),'59, 4');click(wiz,1);assert 'conditions' in text(u.GetDlgItem(wiz,101));settext(u.GetDlgItem(wiz,111),'35');click(wiz,1)
 msg=waitfor('#32770','SAIV IT');assert 'pressure in every measurement' in ' '.join(t for h,t,cl,id in children(msg));dismiss(msg);assert saved()==before;report['failed_conversion_preserves_history']=True
 # Another layout keeps its own settings; reuse asks again only for missing physical conditions.
 surface=ROOT/'data/2026_09_07_19-34-42_C.txt';openfile(main,surface);wiz=waitfor('SITImportChoices')
 for step in range(10):
  title=text(u.GetDlgItem(wiz,101))
  if 'conditions' in title:
   for id,value in [(110,'10'),(111,'35'),(112,'1013.25')]:
    if u.GetDlgItem(wiz,id):settext(u.GetDlgItem(wiz,id),value)
   click(wiz,1);break
  if ': OxR ' in title:select(wiz,102,3)
  click(wiz,1)
 export(waitfor('SITImportData'),'surface_first');assert len(saved())==2
 openfile(main,surface);prompt=waitfor('#32770','Previous conversion');click(prompt,6);wiz=waitfor('SITImportChoices');assert 'conditions' in text(u.GetDlgItem(wiz,101));assert text(u.GetDlgItem(wiz,110))=='' and text(u.GetDlgItem(wiz,111))==''
 for id,value in [(110,'12'),(111,'30'),(112,'1000')]:
  if u.GetDlgItem(wiz,id):settext(u.GetDlgItem(wiz,id),value)
 click(wiz,1);latest=export(waitfor('SITImportData'),'surface_reused');content=latest.read_text(encoding='utf-8-sig');assert 'User-supplied temperature C=12' in content and 'User-supplied salinity=30' in content;report['missing_conditions_requested_again']=True;report['multiple_layouts_remembered']=True
 before=saved()
 # Corrupt history behaves like no saved preset and remains replaceable through a successful conversion.
 with winreg.OpenKey(winreg.HKEY_CURRENT_USER,registry,0,keyAccess) as key:winreg.SetValueEx(key,next(iter(initial)),0,winreg.REG_BINARY,b'broken')
 openfile(main,b);wiz=waitfor('SITImportChoices');click(wiz,2);report['corrupt_history_falls_back_to_wizard']=True
 report['first_export']=str(first);report['reused_export']=str(second);report['isolated_registry']=registry
 (out/'gui_validation.json').write_text(json.dumps(report,indent=2));print('PASS preset GUI: first conversion, restart recognition/date, reuse values/current AP, No/Cancel, changed columns, corrupt history')
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
 try:winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER,registry,winreg.KEY_WOW64_32KEY)
 except FileNotFoundError:pass
