"""Owned-process GUI regression. Test artifacts stay in this project.

Test runtime copies deny registry creation and disable physical serial opening.
Delivered binaries are never patched by this test.
"""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,struct,shutil,hashlib,pefile,sys
from check_startup_windows import k,u,n,SI,PI,CB

R=Path(__file__).resolve().parent.parent
OUT=R/'analysis/runtime_test/batch1412_final'/str(time.time_ns());OUT.mkdir(parents=True)
CUSTOMER=R/'data/dataFormCoustomer';sources=sorted(CUSTOMER.glob('*_C.txt'))
original_hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
u.GetDlgItem.argtypes=[w.HWND,c.c_int];u.GetDlgItem.restype=w.HWND
u.GetDlgCtrlID.argtypes=[w.HWND];u.IsWindow.argtypes=[w.HWND];u.IsWindowEnabled.argtypes=[w.HWND]
k.VirtualProtectEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,c.POINTER(w.DWORD)]
k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.c_void_p]
k.VirtualAllocEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=c.c_void_p
k.ResumeThread.argtypes=[w.HANDLE]
k.CreateRemoteThread.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p,w.DWORD,c.c_void_p];k.CreateRemoteThread.restype=w.HANDLE
k.CreateToolhelp32Snapshot.argtypes=[w.DWORD,w.DWORD];k.CreateToolhelp32Snapshot.restype=w.HANDLE
def text(h,cls=False):
 b=c.create_unicode_buffer(200000);(u.GetClassNameW if cls else u.GetWindowTextW)(h,b,len(b));return b.value
def field(h,id):
 b=c.create_unicode_buffer(200000);u.SendMessageW(u.GetDlgItem(h,id),0xd,len(b),c.addressof(b));return b.value
def children(h):
 rows=[]
 @CB
 def cb(ch,l):rows.append((ch,text(ch),text(ch,True),u.GetDlgCtrlID(ch)));return True
 u.EnumChildWindows(h,cb,0);return rows
def settext(h,s):
 b=c.create_unicode_buffer(str(s));return u.SendMessageW(h,0xc,0,c.addressof(b))
def post(h,id):assert u.PostMessageW(h,0x111,id,0)
def wait(pred,timeout=20):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  value=pred()
  if value:return value
  time.sleep(.03)
 raise AssertionError('Timed out: '+str(app.windows() if 'app' in globals() else 'startup'))
def test_runtime(version):
 folder=OUT/version;folder.mkdir()
 old=version=='1411';source=R/('analysis/single'+version+'/SAIV_IT_Runtime.exe')
 data=bytearray(source.read_bytes());p=pefile.PE(data=bytes(data));last=p.sections[-1]
 align=lambda x,a:(x+a-1)//a*a
 rva=align(last.VirtualAddress+max(last.Misc_VirtualSize,last.SizeOfRawData),16)
 # Test-only in-memory registry: reads report missing values; creates and
 # writes succeed without touching Windows' registry hive files.
 sizes={b'RegCreateKeyExA':36,b'RegOpenKeyExA':20,b'RegSetValueExA':24,b'RegDeleteValueA':8,b'RegDeleteKeyA':8,b'RegQueryValueExA':24,b'RegQueryInfoKeyA':48,b'RegEnumValueA':32,b'RegEnumKeyExA':32,b'RegCloseKey':4,b'RegFlushKey':4}
 entries=[(i.address-p.OPTIONAL_HEADER.ImageBase,i.name) for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name in sizes]
 code=bytearray(b'\x60\xe8\0\0\0\0\x5e\x81\xee'+struct.pack('<I',rva+6))
 patches=[]
 for iat,name in entries:
  patches.append((len(code)+2,name));code+=b'\x8d\x86'+bytes(4)+b'\x89\x86'+struct.pack('<I',iat)
 code+=b'\x61\xe9'+struct.pack('<i',p.OPTIONAL_HEADER.AddressOfEntryPoint-(rva+len(code)+6))
 offsets={}
 for name in sizes:
  offsets[name]=rva+len(code)
  if name==b'RegCreateKeyExA':code+=bytes.fromhex('8b442420c700341200008b44242485c07406c7000100000031c0c22400')
  else:
   result=2 if name in (b'RegOpenKeyExA',b'RegQueryValueExA',b'RegQueryInfoKeyA',b'RegEnumValueA',b'RegEnumKeyExA') else 0
   code+=b'\xb8'+struct.pack('<I',result)+b'\xc2'+struct.pack('<H',sizes[name])
 for off,name in patches:struct.pack_into('<I',code,off,offsets[name])
 raw=last.PointerToRawData+rva-last.VirtualAddress;data.extend(bytes(raw-len(data))+code)
 size=align(len(data)-last.PointerToRawData,p.OPTIONAL_HEADER.FileAlignment);data.extend(bytes(last.PointerToRawData+size-len(data)))
 for off,value in [(last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(code)),(last.get_field_absolute_offset('SizeOfRawData'),size),(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(code),p.OPTIONAL_HEADER.SectionAlignment)),(p.OPTIONAL_HEADER.get_field_absolute_offset('AddressOfEntryPoint'),rva)]:struct.pack_into('<I',data,off,value)
 data[p.get_offset_from_rva(0x7e8f8)]=0xc3 # OpenPort is a no-op in the owned test process.
 exe=folder/'SAIV_IT_Runtime.exe';exe.write_bytes(data)
 dllname='SIT_Import151.dll' if old else 'SIT_Import154.dll'
 shutil.copyfile(R/dllname,folder/dllname)
 return exe,folder/dllname
class App:
 def __init__(self,version):
  exe,self.dll=test_runtime(version);self.pi=PI();self.desktop='SIT_batch_'+str(time.time_ns());self.desk=u.CreateDesktopW(self.desktop,None,None,0,0x1ff,None);assert self.desk
  si=SI();si.cb=c.sizeof(si);si.desktop=self.desktop;si.flags=1;si.show=1
  assert k.CreateProcessW(str(exe),None,None,None,False,0,None,str(exe.parent),c.byref(si),c.byref(self.pi)),c.get_last_error()
 def windows(self):
  rows=[]
  @CB
  def cb(h,l):
   pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
   if pid.value==self.pi.pid and u.IsWindowVisible(h):rows.append((h,text(h),text(h,True)))
   return True
  u.EnumDesktopWindows(self.desk,cb,0);return rows
 def window(self,cls):return next((h for h,t,cl in self.windows() if cl==cls),None)
 def write(self,a,b):
  old=w.DWORD();assert k.VirtualProtectEx(self.pi.process,a,len(b),0x40,c.byref(old));assert k.WriteProcessMemory(self.pi.process,a,b,len(b),None);k.VirtualProtectEx(self.pi.process,a,len(b),old.value,c.byref(old))
 def no_presets(self):
  # Only the loaded conversion DLL's registry imports are denied, preserving
  # Windows' own dialog behavior. This is not a production-code change.
  class Entry(c.Structure):
   _fields_=[('size',w.DWORD),('id',w.DWORD),('pid',w.DWORD),('g',w.DWORD),('p',w.DWORD),('base',c.c_void_p),('bytes',w.DWORD),('module',w.HANDLE),('name',w.WCHAR*256),('path',w.WCHAR*260)]
  k.Module32FirstW.argtypes=[w.HANDLE,c.POINTER(Entry)];k.Module32NextW.argtypes=[w.HANDLE,c.POINTER(Entry)]
  snap=k.CreateToolhelp32Snapshot(0x18,self.pi.pid);entry=Entry();entry.size=c.sizeof(entry);ok=k.Module32FirstW(snap,c.byref(entry));base=None
  while ok:
   if entry.name.lower()==self.dll.name.lower():base=entry.base;break
   ok=k.Module32NextW(snap,c.byref(entry))
  k.CloseHandle(snap);assert base,'Conversion DLL did not load'
  self.dllbase=base
  mem=k.VirtualAllocEx(self.pi.process,None,4096,0x3000,0x40);assert mem
  self.write(mem,b'\xb8\x02\0\0\0\xc2\x14\0');self.write(mem+16,bytes.fromhex('8b442420c700341200008b44242485c07406c7000100000031c0c22400'));self.write(mem+128,b'\x31\xc0\xc2\x18\0')
  pe=pefile.PE(str(self.dll))
  for d in pe.DIRECTORY_ENTRY_IMPORT:
   for i in d.imports:
    if i.name in (b'RegOpenKeyExW',b'RegCreateKeyExW',b'RegSetValueExW'):self.write(base+i.address-pe.OPTIONAL_HEADER.ImageBase,struct.pack('<I',mem+({b'RegOpenKeyExW':0,b'RegCreateKeyExW':16,b'RegSetValueExW':128}[i.name])))
 def close(self):
  k.TerminateProcess(self.pi.process,0);k.WaitForSingleObject(self.pi.process,5000);k.CloseHandle(self.pi.thread);k.CloseHandle(self.pi.process);u.CloseDesktop(self.desk)

def startup(version):
 global app
 app=App(version);main=wait(lambda:app.window('TForm1'));time.sleep(2);app.no_presets()
 for h,t,cl in app.windows():
  if cl=='SITSoftwareUpdate':post(h,306)
 return main

def choose_wizard(wiz,cancel=False):
 pages=[]
 if cancel:post(wiz,2);wait(lambda:not u.IsWindow(wiz));return pages
 while u.IsWindow(wiz):
  time.sleep(.025)
  label=text(u.GetDlgItem(wiz,101))
  if not label:continue
  pages.append(label);combo=u.GetDlgItem(wiz,102)
  if combo:
   choice=1 if any(x in label for x in (': C -',': T -',': P -','OxR','Derived seawater')) else 0
   u.SendMessageW(combo,0x14e,choice,0)
  # Additional questions occur only in explicit missing-conditions tests.
  for id,value in [(110,'10'),(111,'35'),(112,'1013.25')]:
   edit=u.GetDlgItem(wiz,id)
   if edit:settext(edit,value)
  post(wiz,1);wait(lambda:not u.IsWindow(wiz) or text(u.GetDlgItem(wiz,101))!=label)
 return pages

def select_files(main,files,destination):
 button=next(h for h,t,cl,id in children(main) if t.replace('&','')=='Convert')
 assert u.PostMessageW(button,0xf5,0,0)
 dialog=wait(lambda:app.window('#32770'))
 edit=next(h for h,t,cl,id in children(dialog) if cl=='Edit' and id==1148)
 settext(edit,' '.join('"'+str(p)+'"' for p in files));post(dialog,1)
 if len(files)==1:return
 folderdialog=wait(lambda:next((h for h,t,cl in app.windows() if cl=='#32770' and h!=dialog),None))
 settext(u.GetDlgItem(folderdialog,14148),destination);post(folderdialog,1)
 return wait(lambda:app.window('SITBatchConvert'))

def finish_batch(batch,cancel_wizard=False,cancel_after_saved=False):
 wizards=0;pages=[];end=time.monotonic()+120;cancelled=False
 while time.monotonic()<end:
  wiz=app.window('SITImportChoices')
  if wiz:wizards+=1;pages+=choose_wizard(wiz,cancel_wizard)
  if text(u.GetDlgItem(batch,605))=='Close':break
  if cancel_after_saved and not cancelled and 'Saved:' in field(batch,604):
   post(batch,605);cancelled=True
  time.sleep(.005)
 else:raise AssertionError('Batch did not finish: '+str(app.windows()))
 status=text(u.GetDlgItem(batch,601));log=field(batch,604)
 if status=='15 converted, 0 failed, 0 not processed.':
  from capture_window import capture
  capture(batch,OUT/'batch_complete.png',2)
 post(batch,605);wait(lambda:not u.IsWindow(batch))
 return dict(status=status,wizards=wizards,pages=pages,log=log)

def dismiss_preset_warning():
 for h,t,cl in app.windows():
  if cl=='#32770':
   body=' '.join(ct for ch,ct,cc,id in children(h) if cc=='Static')
   if body:
    pass # Expected warning: this test deliberately disables preset persistence.
    if 'Conversion succeeded' in body:
     for button,label,cls,id in children(h):
      if cls=='Button':u.PostMessageW(button,0xf5,0,0)
    else:raise AssertionError(body)

def invoke_single(main,path):
 pe=pefile.PE(str(app.dll));entry=next(e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'SitImport')
 mem=k.VirtualAllocEx(app.pi.process,None,65536,0x3000,0x40);assert mem
 app.write(mem+256,str(path).encode('mbcs')+b'\0')
 # Match the preserved application's UI-thread x87 environment when invoking
 # its unmodified conversion entry on an owned test thread.
 k.SuspendThread.argtypes=[w.HANDLE];k.Wow64GetThreadContext.argtypes=[w.HANDLE,c.c_void_p]
 context=c.create_string_buffer(716);struct.pack_into('<I',context,0,0x10008)
 assert k.SuspendThread(app.pi.thread)!=0xffffffff
 try:assert k.Wow64GetThreadContext(app.pi.thread,context)
 finally:k.ResumeThread(app.pi.thread)
 app.write(mem+1024,struct.pack('<H',struct.unpack_from('<I',context,28)[0]&0xffff))
 code=b'\xd9\x2d'+struct.pack('<I',mem+1024)+b'\x68'+struct.pack('<I',mem+256)+b'\x68'+struct.pack('<I',main)+b'\xb8'+struct.pack('<I',app.dllbase+entry)+b'\xff\xd0\x31\xc0\xc2\x04\0'
 app.write(mem,code);thread=k.CreateRemoteThread(app.pi.process,None,0,mem,None,0,None);assert thread
 return thread

def single_result(path,destination,main,via_picker=False):
 if via_picker:select_files(main,[path],destination.parent);thread=None
 else:thread=invoke_single(main,path)
 choose_wizard(wait(lambda:app.window('SITImportChoices')))
 def result_window():dismiss_preset_warning();return app.window('SITImportData')
 result=wait(result_window);post(result,201)
 save=wait(lambda:next((h for h,t,cl in app.windows() if cl=='#32770' and t=='Export all fields to a new file'),None))
 time.sleep(.2)
 edit=next(h for h,t,cl,id in children(save) if cl=='Edit' and id in (1001,1148,1152))
 u.SendMessageW(save,0x28,edit,1)
 u.SendMessageW(edit,0xb1,0,-1)
 for ch in str(destination):u.SendMessageW(edit,0x102,ord(ch),0)
 u.SendMessageW(save,0x28,u.GetDlgItem(save,1),1)
 u.PostMessageW(u.GetDlgItem(save,1),0xf5,0,0)
 time.sleep(.2)
 wait(lambda:destination.exists())
 msg=wait(lambda:next((h for h,t,cl in app.windows() if cl=='#32770' and any('All fields and metadata were exported.' in ct for ch,ct,cc,id in children(h))),None))
 for button,label,cls,id in children(msg):
  if cls=='Button':u.PostMessageW(button,0xf5,0,0)
 wait(lambda:not u.IsWindow(msg))
 assert u.PostMessageW(result,0x10,0,0);wait(lambda:not u.IsWindow(result))
 if thread:assert k.WaitForSingleObject(thread,5000)==0;k.CloseHandle(thread)
 return destination.read_bytes()

report={}
try:
 main=startup('1412_hw330')
 # The delivered module's manual firmware dialog, with physical serial opening
 # disabled and registry access replaced by in-memory stubs in this test only.
 from capture_window import capture
 post(main,0x7e51);fw=wait(lambda:app.window('SITFirmwareUpdate'))
 assert 'hardware 3.1.2 and 3.3.0' in field(fw,507)
 assert 'selected automatically' in field(fw,507)
 assert not u.IsWindowEnabled(u.GetDlgItem(fw,505))
 capture(fw,OUT/'firmware_prompt.png',2)
 u.MoveWindow.argtypes=[w.HWND,c.c_int,c.c_int,c.c_int,c.c_int,w.BOOL]
 u.MoveWindow(fw,60,60,680,490,True);time.sleep(.2)
 capture(fw,OUT/'firmware_minimum.png',2)
 post(fw,504);wait(lambda:'Connect the logger in SIT first' in field(fw,502))
 assert not u.IsWindowEnabled(u.GetDlgItem(fw,505))
 capture(fw,OUT/'firmware_no_connection.png',2)
 post(fw,506);wait(lambda:not u.IsWindow(fw));assert u.IsWindowEnabled(main)
 post(main,0x7e41);sw=wait(lambda:app.window('SITSoftwareUpdate'))
 assert '1.4.12' in field(sw,301),field(sw,301)
 post(sw,306);wait(lambda:not u.IsWindow(sw))
 report['firmware_gui']={'both_hardware_revisions_shown':True,'automatic_selection_explained':True,'update_disabled_without_verified_device':True,'close_restores_main':True,'software_version':'1.4.12'}
 print('PASS firmware GUI, both hardware labels and missing-device error',flush=True)
 destination=OUT/'converted';destination.mkdir()
 batch=select_files(main,sources[:2],destination);report['customer_batch']=finish_batch(batch)
 assert report['customer_batch']['status']=='2 converted, 0 failed, 0 not processed.'
 prior=R/'analysis/runtime_test/batch1413/1793186361589692300/baseline1411'
 for path in sources[:2]:
  output=destination/(path.stem+'_SIT.txt')
  assert output.read_bytes()==(prior/output.name).read_bytes()
 report['tested_module_sha256']=hashlib.sha256(app.dll.read_bytes()).hexdigest()
 report['tested_runtime']='analysis/single1412_hw330/SAIV_IT_Runtime.exe'
 report['source_files_unchanged']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==digest for p,digest in original_hashes.items())
 report['passed']=True
 (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('PASS final 1.4.12: hardware dialog, software version, two-file batch and export equality',OUT,flush=True)
finally:
 if app:app.close()
