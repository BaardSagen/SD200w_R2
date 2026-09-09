from pathlib import Path
import sys,json,struct
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
R=Path(__file__).resolve().parent.parent;m=json.loads((R/'analysis/last_com_port_manifest.json').read_text());results=[]
for base in [0x400000,0x1400000]:
 for case in ['port7','port11','port255','zero','ip','no_form','no_comm','no_registry']:
  p=pefile.PE(str(R/m['output']));p.relocate_image(base);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x20000)
  form=0x10001000;comm=0x10003000;registry=0x10008000;vmt=0x10009000;writer=0x1000a000;frame=0x1000c000;sp=0x10010000
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return int.from_bytes(u.mem_read(a,4),'little')
  def string(a):return bytes(u.mem_read(a,get(a-4))).decode()
  port={'port7':7,'port11':11,'port255':255,'zero':0}.get(case,7)
  put(base+0x1c8964,0 if case=='no_form' else form);put(form+0x510,0 if case=='no_comm' else comm);u.mem_write(comm+0x34,bytes([port]));u.mem_write(comm+0x407e,bytes([case=='ip']));put(frame-0x18,0 if case=='no_registry' else registry);put(registry,vmt);put(vmt+12,writer)
  regs={UC_X86_REG_EAX:123,UC_X86_REG_EBX:456,UC_X86_REG_ECX:789,UC_X86_REG_EDX:987,UC_X86_REG_ESI:654,UC_X86_REG_EDI:321,UC_X86_REG_ESP:sp,UC_X86_REG_EBP:frame,UC_X86_REG_EFLAGS:0x246}
  for reg,val in regs.items():u.reg_write(reg,val)
  calls=[]
  def hook(u,a,n,d):
   if a==base+m['previous_rva']:u.emu_stop()
   elif a==writer:
    st=u.reg_read(UC_X86_REG_ESP);calls.append((string(u.reg_read(UC_X86_REG_EDX)),string(u.reg_read(UC_X86_REG_ECX)),get(st+4)))
    u.reg_write(UC_X86_REG_EIP,get(st));u.reg_write(UC_X86_REG_ESP,st+8)
    for reg in [UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX]:u.reg_write(reg,0xdeadbeef)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+m['rva'],base+p.OPTIONAL_HEADER.SizeOfImage,count=1000)
  assert calls==([('Comm','Port',port)] if case.startswith('port') else []),(case,calls)
  assert all(u.reg_read(reg)==val for reg,val in regs.items()),case
  assert u.reg_read(UC_X86_REG_EIP)==base+m['previous_rva'];results.append(dict(base=hex(base),case=case,writes=calls))
(R/'analysis/last_com_port_validation.json').write_text(json.dumps(results,indent=2));print('PASS',len(results),'port persistence/register/stack/ASLR guards')
