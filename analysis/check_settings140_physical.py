"""User-authorized physical GUI setting tests on COM7 and COM11 only."""
from native140_gui_support import *
import re,struct,subprocess,pefile
report=[]
def read(a,size=4):
 buf=c.create_string_buffer(size);assert k.ReadProcessMemory(pi.process,a,buf,size,None);return buf.raw
def d(a):return int.from_bytes(read(a),'little')
def astr(at):
 ptr=d(at);return read(ptr,min(d(ptr-4),16384)).decode('latin1') if ptr else ''
def push(obj):
 parent=d(obj+0x24);x=d(obj+0x30)+d(obj+0x38)//2;y=d(obj+0x34)+d(obj+0x3c)//2;u.PostMessageW(d(parent+0x14c),0x201,1,x|(y<<16));u.PostMessageW(d(parent+0x14c),0x202,0,x|(y<<16))
def save(): (ROOT/'analysis/runtime_test/settings140/physical_gui_validation.json').write_text(json.dumps(report,indent=2))
try:
 main=waitfor('TForm1');time.sleep(1);peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=d(peb.value+8);form=d(base+0x1c8964)
 ldr=d(peb.value+12);head=ldr+20;node=d(head);dllbase=0
 while node!=head:
  name=read(d(node+40),int.from_bytes(read(node+36,2),'little')).decode('utf-16le')
  if name.lower()=='sit_import140.dll':dllbase=d(node+16);break
  node=d(node)
 dll=pefile.PE(str(ROOT/'SIT_Import140.dll'));symbols={x.split()[-1]:int(x.split()[0],16)-dll.OPTIONAL_HEADER.ImageBase for x in subprocess.check_output(['nm',str(ROOT/'SIT_Import140.dll')],text=True).splitlines() if len(x.split())==3 and x.split()[0].isalnum()}
 rxname=next(k for k in symbols if 'settingsRx' in k and 'At' not in k)
 def rx():
  at=dllbase+symbols[rxname];ptr=d(at);length=d(at+4);return read(ptr,min(length,65536)).decode('latin1') if ptr and length else ''
 for port,interval,zone in ([(11,1,'GMT')] if '--port11' in sys.argv else [(7,2,'GMT'),(11,1,'LT')]):
  push(d(form+0x4ec));deadline=time.monotonic()+35;selected=False
  while time.monotonic()<deadline:
   time.sleep(.25);detect=d(d(base+0x1b1e1c));arr=d(detect+0x330) if detect else 0
   if not arr or not u.IsWindowVisible(d(detect+0x14c)):continue
   for row in range(d(arr-4)):
    worker=d(arr+20*row);name=astr(arr+20*row+4)
    if name.lower()=='com'+str(port) and read(worker+0x71,1)==b'\2' and read(worker+0x60,1)==b'\0':
     report.append(dict(port=port,phase='detected',identity=astr(worker+0x5c)));listing=d(detect+0x2e4);lh=d(d(listing+0x248)+0x14c);xy=20|((8+16*row)<<16);u.PostMessageW(lh,0x201,1,xy);u.PostMessageW(lh,0x202,0,xy);time.sleep(.2);u.PostMessageW(d(d(detect+0x2d0)+0x14c),0xf5,0,0);selected=True;break
   if selected:break
  assert selected,'Detect did not find COM'+str(port);time.sleep(2);assert not u.IsWindowVisible(d(detect+0x14c));save()
  for caption,clockmode in ([('TIME/D&ATE',True)] if '--clock-only' in sys.argv else [('&Interval',False),('TIME/D&ATE',True)]):
   button=next(h for h,t,cl,i in children(main) if t==caption);u.IsWindowEnabled.argtypes=[w.HWND];assert u.IsWindowEnabled(button),(port,caption,'disabled',read(d(form+0x510)+0x24,48).hex(),{key:d(dllbase+value) for key,value in symbols.items() if any(key.endswith(x) for x in ['settingsKind','settingsPort','settingsBusy','settingsDialog','settingsMain'])});u.PostMessageW(button,0xf5,0,0);dialog=waitfor('SITDeviceSettings')
   if clockmode:
    u.SendMessageW(u.GetDlgItem(dialog,101),0xf1,zone=='LT',0);u.SendMessageW(u.GetDlgItem(dialog,102),0xf1,zone=='GMT',0)
   else:u.SendMessageW(u.GetDlgItem(dialog,101),0x14e,0 if interval==1 else 1,0)
   u.PostMessageW(dialog,0x111,1,0);deadline=time.monotonic()+120;message=None;trace=[];previous=''
   while time.monotonic()<deadline:
    time.sleep(.02);current=rx()
    if current!=previous:trace.append(current);previous=current
    matches=[h for h,t,cl in windows() if cl=='#32770']
    if matches:
     message=matches[0];break
   assert message,(port,caption,'No completion',rx());body='\n'.join(t for h,t,cl,i in children(message) if cl=='Static');passed=('SD200 clock verified.' in body and ('Logger clock verified.' in body if port==11 else True)) if clockmode else 'SD200 measuring interval verified.' in body
   report.append(dict(port=port,phase='clock' if clockmode else 'interval',interval=interval,zone=zone,passed=passed,message=body,receive_trace=trace));save();print(port,caption,body,flush=True);ok=next((ch,id) for ch,txt,cl,id in children(message) if cl=='Button' and txt.replace('&','').upper()=='OK');u.SendMessageW(message,0x111,ok[1],ok[0]);time.sleep(.3);u.PostMessageW(dialog,0x111,2,0);time.sleep(1);assert passed,(port,caption,body)
except Exception as e:report.append(dict(error=str(e)));save();raise
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
