"""Run original search index transitions and actual serial parameter selection."""
from pathlib import Path
import json,struct,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'analysis'/'python_packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
reports=[]
for base in (0x400000,0x1400000):
 p=pefile.PE(str(ROOT/'SD200W_SAIV_OSU107_Detect_Priority.exe'))
 if base!=0x400000:p.relocate_image(base)
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage)
 u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x10000)
 obj=0x10001000;array=0x10002004;port=0x10003000;stack=0x10008000
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 put(obj+0x30,array);put(array-4,8);put(obj+0x64,port)
 u.mem_write(array,bytes(p.get_data(0x1b13b4,32)));u.mem_write(obj+0x60,b'\1')
 u.reg_write(UC_X86_REG_EBX,obj);u.reg_write(UC_X86_REG_ESP,stack)
 attempts=[];current={}
 def ret():
  sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4)
 def hook(uc,a,size,data):
  if a==base+0x58ec:
   u.reg_write(UC_X86_REG_EAX,get(u.reg_read(UC_X86_REG_EAX)-4)-1);ret()
  elif a in (base+0x7e6bc,base+0x7e750):
   assert u.reg_read(UC_X86_REG_EAX)==port
   value=u.reg_read(UC_X86_REG_EDX)
   if a==base+0x7e6bc:current['baud']=value
   else:current['parity']=chr(value&255)
   ret()
 u.hook_add(UC_HOOK_CODE,hook)
 for i in range(16):
  u.emu_start(base+0x103926,base+0x103948,count=100)
  attempts.append(current.copy())
  u.emu_start(base+0x10367b,base+0x1036bb,count=100)
 expected=[dict(baud=r,parity=q) for r in (9600,4800,2400,19200,38400,1200,600,300) for q in 'ne']
 assert attempts==expected,(attempts,expected)
 assert bytes(u.mem_read(obj+0x60,1))==b'\0'
 assert u.reg_read(UC_X86_REG_ESP)==stack
 reports.append(dict(base=hex(base),attempts=attempts,stops_after_full_pass=True))
(ROOT/'analysis'/'detect_priority_validation.json').write_text(json.dumps(dict(result='PASS',cases=reports),indent=2))
print('PASS: all 16 serial settings in requested order, loop termination and relocated image.')
