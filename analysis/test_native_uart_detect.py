"""Execute the real x86 Detect probe with mocked serial/time APIs, no hardware."""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'analysis/python_packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
m=json.loads((R/'analysis/native_uart_detect_manifest.json').read_text())
STARTUP='Stored air pressure(mb):AP= 947.76709\r\nChange air pressure <A>\r\nStatus/Start/Menu <S>\r\nPassive <H>\r\nIf no command, measurement will start in 10 sec.\r\n'
STOP=STARTUP.replace('measurement will start in 10 sec.','instrument will go passive in 10 sec.')
STATUS='Status:\r\nModel SD204,Ser No 1756\r\nInterval: 2sec\r\nStart by Mag-Key or press <I>\r\nor\r\nPress <M> for menu or wait 10sec\r\n'
MAIN='Menu:\r\nMeasuring interval <I>\r\nDump stored data to screen <F>\r\nErase data in memory <E>\r\nSet coefficients <M>\r\nStart via key-board <R>\r\nExit (passive) <H>\r\n'
INTERVAL='Current set up:\r\nMeasuring interval    2sec \r\nChange: Y/N Menu: <G>\r\n'
IMAGES={}
class Harness:
 def __init__(self,base,scenario,split=None):
  if base not in IMAGES:
   p=pefile.PE(str(R/m['output']));p.relocate_image(base);IMAGES[base]=(p.OPTIONAL_HEADER.SizeOfImage,bytes(p.get_memory_mapped_image()))
  size,loaded=IMAGES[base];self.u=u=Uc(UC_ARCH_X86,UC_MODE_32);self.base=base;u.mem_map(base,size);u.mem_write(base,loaded);u.mem_map(0x10000000,0x400000)
  self.obj=0x10001000;self.comm=0x10002000;self.stack=0x10008000;self.frame=0x10007000;self.stop=0x10009000;self.pool=0x10100000;self.clock=0;self.lastRx=0;self.tx=[];self.closed=False;self.scenario=scenario
  self.put(self.obj+0x64,self.comm);self.put(self.comm+0x30,9600);u.mem_write(self.comm+0x4c,b'n');u.mem_write(self.obj+0x60,b'\1');self.put(self.stack,self.stop)
  self.put(base+0x1c93f4,0x1000a000);self.put(base+0x1c9358,0x1000a010)
  self.events=[]
  if scenario=='interval_menu':self.schedule(40,INTERVAL,split)
  if scenario=='main':self.schedule(40,MAIN,split)
  if scenario=='stop_menu':self.schedule(40,STOP,split)
  if scenario=='startup':self.schedule(40,STARTUP,split)
  if scenario=='surface':self.schedule(40,'SAIV110 Surface logger SN107, Ver: 0.9.9P\r\n',split)
  if scenario=='logger':self.schedule(40,'OSU107 Instrument logger SN107, Ver: 0.9.9P\r\n',split)
  if scenario=='running':self.schedule(40,'N00001 S35.0 T10.2 P1.0 OX95.0\r\n',split)
  if scenario.startswith('parity'):
   self.events=[(40,'\x8d\n')]
   if scenario=='parity':self.schedule(80,STARTUP)
  if scenario=='unknown':self.schedule(40,'Unrecognised device output\r\n',split)
  for reg,val in [(UC_X86_REG_EBX,self.obj),(UC_X86_REG_EBP,self.frame),(UC_X86_REG_ESI,0x12345678),(UC_X86_REG_EDI,0x23456789),(UC_X86_REG_ESP,self.stack)]:u.reg_write(reg,val)
  for address in [self.stop,0x1000a000,0x1000a010]+[self.base+x for x in [0x7fbc0,0x4220,0x3fec,0x3f98,0x7f9c4,0x7ffc4,0x796c,0x293000]]:u.hook_add(UC_HOOK_CODE,self.hook,begin=address,end=address)
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def get(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def alloc(self,b):
  if isinstance(b,str):b=b.encode('latin1')
  a=self.pool;self.pool+=(len(b)+12+3)&~3;self.u.mem_write(a,struct.pack('<iI',-1,len(b))+b+b'\0');return a+8
 def string(self,a):return bytes(self.u.mem_read(a,self.get(a-4))) if a else b''
 def schedule(self,t,s,split=None):
  if split is None:split=len(s)//2
  self.events.extend([(t,s[:split]),(t+400,s[split:])]);self.events.sort()
 def ret(self,n=0):sp=self.u.reg_read(UC_X86_REG_ESP);self.u.reg_write(UC_X86_REG_EIP,self.get(sp));self.u.reg_write(UC_X86_REG_ESP,sp+4+n)
 def hook(self,u,a,size,data):
  if a==self.stop:u.emu_stop();return
  if a not in (0x1000a000,0x1000a010,self.base+0x7fbc0,self.base+0x4220,self.base+0x3fec,self.base+0x3f98,self.base+0x7f9c4,self.base+0x7ffc4,self.base+0x796c,self.base+0x293000):return
  eax=u.reg_read(UC_X86_REG_EAX);edx=u.reg_read(UC_X86_REG_EDX)
  if a==0x1000a000:u.reg_write(UC_X86_REG_EAX,self.clock);self.ret()
  elif a==0x1000a010:
   self.clock+=self.get(u.reg_read(UC_X86_REG_ESP)+4)
   if self.scenario=='cancel' and self.clock>=700:u.mem_write(self.obj+0xc,b'\1')
   self.ret(4)
  elif a in (self.base+0x796c,self.base+0x293000):
   sp=u.reg_read(UC_X86_REG_ESP);ptr=self.get(sp+8)
   if a==self.base+0x796c:
    assert self.get(ptr)==28
    u.mem_write(ptr+18,bytes([8,0,0]))
   else:assert bytes(u.mem_read(ptr+18,3))==bytes([7,2,0])
   fail=(self.scenario=='parity_getfail' and a==self.base+0x796c) or (self.scenario=='parity_setfail' and a==self.base+0x293000)
   u.reg_write(UC_X86_REG_EAX,0 if fail else 1);self.ret(8)
  elif a==self.base+0x7fbc0:
   assert eax==self.comm
   if self.events and self.events[0][0]<=self.clock:
    _,s=self.events.pop(0);self.put(edx,self.alloc(s));u.reg_write(UC_X86_REG_EAX,1);self.lastRx=self.clock
   else:u.reg_write(UC_X86_REG_EAX,0)
   self.ret()
  elif a==self.base+0x4220:self.put(eax,self.alloc(self.string(self.get(eax))+self.string(edx)));self.ret()
  elif a==self.base+0x3fec:self.put(eax,edx);self.ret()
  elif a==self.base+0x3f98:self.put(eax,0);self.ret()
  elif a==self.base+0x7f9c4:self.closed=True;self.ret()
  elif a==self.base+0x7ffc4:
   command=self.string(edx).decode();assert self.clock-self.lastRx>=250,(self.clock,self.lastRx,command);self.tx.append((self.clock,command))
   if command=='G' and (self.scenario in ('already_main','interval_menu') or (self.scenario=='silent_main' and len(self.tx)>1)):self.schedule(self.clock+60,MAIN)
   if command=='I' and self.scenario=='silent_main':self.schedule(self.clock+40,INTERVAL)
   if command=='I' and self.scenario=='running':self.schedule(self.clock+40,STOP)
   if command=='I' and self.scenario=='sleeping':self.schedule(self.clock+40,STARTUP)
   if command=='S':self.schedule(self.clock+40,STATUS)
   if command=='M':self.schedule(self.clock+40,MAIN)
   self.ret()
 def run(self):
  self.u.emu_start(self.base+m['rva'],self.stop,count=50000000)
  assert self.u.reg_read(UC_X86_REG_EIP)==self.stop,(self.scenario,self.clock,hex(self.u.reg_read(UC_X86_REG_EIP)),self.tx)
  assert self.u.reg_read(UC_X86_REG_ESP)==self.stack+4
  assert self.u.reg_read(UC_X86_REG_EBX)==self.obj
  assert self.u.reg_read(UC_X86_REG_ESI)==0x12345678 and self.u.reg_read(UC_X86_REG_EDI)==0x23456789
  if self.scenario=='empty':
   times=[t for t,s in self.tx if s=='I'];assert len(times)>100 and all(b-a==50 for a,b in zip(times,times[1:])),times
  found=bytes(self.u.mem_read(self.obj+0x62,1))==b'\1'
  commands=[s for t,s in self.tx]
  expected={'interval_menu':['G'],'silent_main':['G','I','G'],'main':[],'startup':['S','M'],'logger':[],'surface':[],'running':['I','S','M'],'stop_menu':['S','M'],'already_main':['G'],'sleeping':['G','I','S','M'],'unknown':[],'cancel':[],'parity':['S','M'],'parity_getfail':[],'parity_setfail':[]}
  if self.scenario in expected:assert commands==expected[self.scenario],(self.scenario,commands)
  assert found==(self.scenario not in ['empty','unknown','cancel','parity_getfail','parity_setfail']),self.scenario
  if self.scenario=='parity':assert self.get(self.obj+0x40)==1 and not self.closed
  if found:assert self.get(self.obj+0x6c)==9600 and bytes(self.u.mem_read(self.obj+0x70,2))==(b'e\2' if self.scenario=='parity' else b'n\2')
  return dict(scenario=self.scenario,base=hex(self.base),split=getattr(self,'split',None),found=found,tx=self.tx,elapsed_ms=self.clock)
results=[]
for base in [0x400000,0x1400000]:
 for scenario in ['interval_menu','silent_main','main','startup','logger','surface','running','already_main','sleeping','unknown','empty','cancel','parity','parity_getfail','parity_setfail','stop_menu']:
  print(hex(base),scenario,flush=True);results.append(Harness(base,scenario).run())
# Exercise all main-menu and startup-menu split boundaries.
for scenario,text in [('main',MAIN),('startup',STARTUP),('stop_menu',STOP),('interval_menu',INTERVAL)]:
 for split in range(1,len(text)):
  h=Harness(0x400000,scenario,split);h.split=split;results.append(h.run())
(R/'analysis/native_uart_detect_validation.json').write_text(json.dumps(dict(result='PASS',cases=len(results),details=results),indent=2))
print('PASS',len(results),'x86 scenarios; 250 ms quiet time, cancellation, stack/registers and relocation verified')
