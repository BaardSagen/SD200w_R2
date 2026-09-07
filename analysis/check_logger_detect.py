from pathlib import Path
import json,struct,sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'analysis'/'python_packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
m=json.loads((ROOT/'analysis'/'logger_detect_manifest.json').read_text());reports=[]
cases=[('osu',[b'\r\nOSU107 Instrument logger SN107, Ver: 0.9.9Q\r\n'],1),('surface',[b'SAIV110 Surface logger SN107, Ver: 0.9.9Q\r\n'],2),('split',[b'OSU107 Instr',b'ument log',b'ger SN107\r\n'],1),('lower',[b'saiv110 surface logger SN107\n'],2),('unknown',[b'Unknown device\r\n'],0),('silent',[],0)]
for base in (0x400000,0x1400000):
 for name,chunks,kind in cases:
  p=pefile.PE(str(ROOT/m['output']))
  if base!=0x400000:p.relocate_image(base)
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage)
  u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x20000)
  obj=0x10001000;port=0x10002000;frame=0x10003000;stack=0x10004000;stop=0x10005000
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def string(a):
   if not a:return b''
   data=bytearray()
   while (ch:=bytes(u.mem_read(a+len(data),1)))!=b'\0':data.extend(ch)
   return bytes(data)
  def save(addr,data):u.mem_write(addr,data+b'\0')
  put(obj+0x64,port);put(port+0x30,9600);u.mem_write(port+0x4c,b'n');u.mem_write(obj+0x60,b'\1')
  put(stack,stop)
  put(base+0x1c9474,0x10005100);put(base+0x1c9384,0x10005200)
  for r,v in ((UC_X86_REG_ESP,stack),(UC_X86_REG_EBP,frame),(UC_X86_REG_EBX,obj),(UC_X86_REG_EAX,port),(UC_X86_REG_EDX,base+0x103cdc),(UC_X86_REG_ESI,0x9876),(UC_X86_REG_EDI,0x7654)):
   u.reg_write(r,v)
  pending=list(chunks);writes=[];sleep_count=[];assigned=[]
  def ret(extra=0):
   sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4+extra)
  def hook(uc,a,size,data):
   if a==0x10005100:
    dcb=get(u.reg_read(UC_X86_REG_ESP)+8);put(dcb+8,0x1001);u.reg_write(UC_X86_REG_EAX,1);ret(8)
   elif a==0x10005200:
    dcb=get(u.reg_read(UC_X86_REG_ESP)+8);assert get(dcb+8) in (0x1001,0x1011)
    u.reg_write(UC_X86_REG_EAX,1);ret(8)
   elif a==base+0x7fbc0:
    if pending:
     chunk=pending.pop(0);save(0x10006000,chunk);put(u.reg_read(UC_X86_REG_EDX),0x10006000);u.reg_write(UC_X86_REG_EAX,1)
    else:u.reg_write(UC_X86_REG_EAX,0)
    ret()
   elif a==base+0x4220:
    dest=u.reg_read(UC_X86_REG_EAX);data=string(get(dest))+string(u.reg_read(UC_X86_REG_EDX));save(0x10008000,data);put(dest,0x10008000);ret()
   elif a==base+0x3fec:
    data=string(u.reg_read(UC_X86_REG_EDX));assigned.append(data);put(u.reg_read(UC_X86_REG_EAX),u.reg_read(UC_X86_REG_EDX));ret()
   elif a==base+0x7bb4:sleep_count.append(20);ret(4)
   elif a==base+0x7ffc4:writes.append(string(u.reg_read(UC_X86_REG_EDX)));ret()
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(base+m['rva'],stop,count=1000000)
  assert writes==([] if kind else [b'AT\r\n']),(name,writes)
  assert (bytes(u.mem_read(obj+0x60,1))==b'\0')==bool(kind)
  assert get(obj+0x6c)==(9600 if kind else 0)
  assert u.reg_read(UC_X86_REG_ESP)==stack+4
  assert u.reg_read(UC_X86_REG_ESI)==0x9876 and u.reg_read(UC_X86_REG_EDI)==0x7654
  if kind:
   assert bytes(u.mem_read(obj+0x62,1))==b'\1'
   assert bytes(u.mem_read(obj+0x71,1))==b'\2'
   put(stack,stop);u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EAX,obj);u.reg_write(UC_X86_REG_EDX,frame-8)
   u.emu_start(base+0x1031b0,stop,count=100000)
   assert assigned[-1]==(b'OSU107' if kind==1 else b'SAIV110'),assigned
  else:assert len(sleep_count)==75
  reports.append(dict(base=hex(base),case=name,writes=[s.decode() for s in writes],kind=kind))
(ROOT/'analysis'/'logger_detect_validation.json').write_text(json.dumps(dict(result='PASS',cases=reports),indent=2));print('PASS: both logger banners, split/case variants, labels, silent/unknown fallback, and relocated image; no transmitted bytes for detected loggers.')
