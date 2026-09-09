"""GUI regression with isolated registry and serial opening disabled in owned processes."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import time,json,struct,winreg,uuid
from check_startup_windows import k,u,n,SI,PI,CB
R=Path(__file__).resolve().parent.parent;OUT=R/'analysis/runtime_test/last_port132';OUT.mkdir(exist_ok=True)
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.c_void_p]
k.VirtualProtectEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,c.POINTER(w.DWORD)]
k.VirtualAllocEx.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=c.c_void_p
k.CreateRemoteThread.argtypes=[w.HANDLE,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p,w.DWORD,c.c_void_p];k.CreateRemoteThread.restype=w.HANDLE
k.ResumeThread.argtypes=[w.HANDLE]
key='T'+uuid.uuid4().hex[:6];root='Software\\MHP\\'+key;access=winreg.KEY_ALL_ACCESS|winreg.KEY_WOW64_32KEY
with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,root+'\\Comm',0,access) as reg:
 winreg.SetValueEx(reg,'Port',0,winreg.REG_DWORD,11);winreg.SetValueEx(reg,'Sd200Baud',0,winreg.REG_DWORD,9600)
def stored():
 with winreg.OpenKey(winreg.HKEY_CURRENT_USER,root+'\\Comm',0,access) as reg:return winreg.QueryValueEx(reg,'Port')[0]
def text(h):
 b=c.create_unicode_buffer(500);u.GetWindowTextW(h,b,500);return b.value
class App:
 def __init__(self,version):
  self.pi=PI();self.deskname='SIT_lastport_'+str(time.time_ns());self.desk=u.CreateDesktopW(self.deskname,None,None,0,0x1ff,None);assert self.desk
  si=SI();si.cb=c.sizeof(si);si.desktop=self.deskname;si.flags=1;si.show=1
  exe=R/('SAIV_Instrument_Terminal_v'+version+'_Sept2026.exe')
  assert k.CreateProcessW(str(exe),None,None,None,False,4,None,str(OUT),c.byref(si),c.byref(self.pi))
  try:
   peb=c.c_size_t();assert n.NtQueryInformationProcess(self.pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;self.base=self.d(peb.value+8)
   self.write(self.base+0x197804,key.encode()+b'\0');self.write(self.base+0x197814,('\\'+root).encode()+b'\0')
   # All calls to OpenPort return without touching physical COM hardware.
   self.write(self.base+0x7e8f8,b'\xc3')
   k.ResumeThread(self.pi.thread)
   end=time.monotonic()+12
   while time.monotonic()<end:
    self.form=self.d(self.base+0x1c8964)
    if self.form and self.d(self.form+0xc4c):break
    time.sleep(.1)
   else:raise AssertionError('startup timeout')
   time.sleep(7);self.comm=self.d(self.form+0x510);self.main=self.d(self.form+0x14c)
  except: self.close();raise
 def read(self,a,count=4):
  b=c.create_string_buffer(count);assert k.ReadProcessMemory(self.pi.process,a,b,count,None);return b.raw
 def d(self,a):return int.from_bytes(self.read(a),'little')
 def write(self,a,b):
  old=w.DWORD();assert k.VirtualProtectEx(self.pi.process,a,len(b),0x40,c.byref(old));assert k.WriteProcessMemory(self.pi.process,a,b,len(b),None)
  k.VirtualProtectEx(self.pi.process,a,len(b),old.value,c.byref(old))
 def port(self):return self.read(self.comm+0x34,1)[0]
 def button(self,parent,name):
  matches=[];seen=[]
  @CB
  def enum(h,l):
   seen.append(text(h))
   if text(h).replace('&','')==name:matches.append(h)
   return True
  u.EnumChildWindows(parent,enum,0);assert len(matches)==1,(name,matches,seen);u.PostMessageW(matches[0],0xf5,0,0);time.sleep(.4)
 def setup(self):
  self.button(self.main,'Setup');self.setupobj=self.d(self.d(self.base+0x1b1b58));self.sh=self.d(self.setupobj+0x14c);assert u.IsWindowVisible(self.sh);return self.sh
 def preset(self,port):
  # Reproduce Detect's already-applied port using the original native setter.
  mem=k.VirtualAllocEx(self.pi.process,None,4096,0x3000,0x40);assert mem
  code=b'\xb8'+struct.pack('<I',self.comm)+b'\xb2'+bytes([port])+b'\xb9'+struct.pack('<I',self.base+0x7e6c0)+b'\xff\xd1\x31\xc0\xc2\x04\x00';self.write(mem,code)
  th=k.CreateRemoteThread(self.pi.process,None,0,mem,None,0,None);assert th;assert k.WaitForSingleObject(th,5000)==0;k.CloseHandle(th);assert self.port()==port
 def select(self,port):
  combo=self.d(self.d(self.setupobj+0x2f8)+0x14c);count=u.SendMessageW(combo,0x146,0,0);values=[]
  for i in range(count):
   b=c.create_unicode_buffer(500);u.SendMessageW(combo,0x148,i,c.addressof(b));values.append(b.value)
  idx=next(i for i,v in enumerate(values) if v.upper()=='COM'+str(port));u.SendMessageW(combo,0x14e,idx,0)
 def close(self):
  k.TerminateProcess(self.pi.process,0);k.WaitForSingleObject(self.pi.process,5000);k.CloseHandle(self.pi.thread);k.CloseHandle(self.pi.process);u.CloseDesktop(self.desk)
results=[]
def run(version,action):
 app=App(version)
 try:action(app)
 finally:app.close()
try:
 def baseline(a):
  assert a.port()==11;a.preset(7);a.setup();a.button(a.sh,'OK');assert stored()==11;results.append('1.3.1 reproduced: COM7 active but stored COM11')
 run('1.3.1',baseline)
 def fixed(a):
  assert a.port()==11;a.preset(7);a.setup();a.button(a.sh,'OK');assert stored()==7;results.append('1.3.2 saves already-applied COM7')
 run('1.3.2',fixed)
 def restart_cancel(a):
  assert a.port()==7;a.setup();a.select(11);a.button(a.sh,'Cancel');assert stored()==7 and a.port()==7;results.append('Restart reads COM7; Cancel preserves COM7')
 run('1.3.2',restart_cancel)
 def manual(a):
  assert a.port()==7;a.setup();a.select(11);a.button(a.sh,'OK');assert stored()==11 and a.port()==11;results.append('Manual selection saves COM11')
 run('1.3.2',manual)
 def again(a):
  assert a.port()==11;results.append('Second restart reads COM11')
 run('1.3.2',again)
 (OUT/'gui_validation.json').write_text(json.dumps(dict(results=results,isolated_registry=root,physical_serial_disabled=True),indent=2));print('PASS',results)
finally:
 # Delete only this randomly named test registry tree, never the user's SdInstr key.
 def remove(path):
  assert path==root or path.startswith(root+'\\')
  with winreg.OpenKey(winreg.HKEY_CURRENT_USER,path,0,access) as reg:
   children=[];i=0
   while True:
    try:children.append(winreg.EnumKey(reg,i));i+=1
    except OSError:break
  for child in children:remove(path+'\\'+child)
  winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER,path,winreg.KEY_WOW64_32KEY)
 remove(root)
