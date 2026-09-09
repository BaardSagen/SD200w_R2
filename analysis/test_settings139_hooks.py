"""Exercise settings gateways at normal/relocated image bases, including fall-through."""
from pathlib import Path
import sys,json,struct
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
R=Path(__file__).resolve().parent.parent;m=json.loads((R/'analysis/settings139_manifest.json').read_text());checks=0
for base in [0x400000,0x1400000]:
 p=pefile.PE(str(R/'analysis/single139/SAIV_IT_Runtime.exe'));p.relocate_image(base);mapped=bytes(p.get_memory_mapped_image())
 for at,label,opcode,old,op in m['patches']:
  for handled in ([0,1] if label in ['settings','download'] else [0]):
   u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,mapped);u.mem_map(0x10000000,0x20000);sp=0x10010000;ret=0x1001f000;seen=[];oldseen=[]
   def put(a,v):u.mem_write(a,struct.pack('<I',v))
   def get(a):return int.from_bytes(u.mem_read(a,4),'little')
   put(sp,ret);put(0x10008000,0x5a)
   regs={UC_X86_REG_EAX:0x10008000 if label=='receive' else 123,UC_X86_REG_EDX:1 if label=='receive' else 456,UC_X86_REG_ECX:789,UC_X86_REG_EBX:111,UC_X86_REG_ESI:222,UC_X86_REG_EDI:333,UC_X86_REG_EBP:444,UC_X86_REG_ESP:sp,UC_X86_REG_EFLAGS:0x246}
   for reg,value in regs.items():u.reg_write(reg,value)
   def hook(u,a,n,arg):
    if a==base+m['dispatch']:
     stack=u.reg_read(UC_X86_REG_ESP);seen.append([get(stack+i) for i in [4,8,12,16]]);u.reg_write(UC_X86_REG_EIP,get(stack));u.reg_write(UC_X86_REG_ESP,stack+20)
     for reg in [UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX]:u.reg_write(reg,0xdeadbeef)
     u.reg_write(UC_X86_REG_EAX,handled)
    elif a==base+old:
     oldseen.append(a)
     if label=='selected':
      stack=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,1);u.reg_write(UC_X86_REG_EIP,get(stack));u.reg_write(UC_X86_REG_ESP,stack+4)
     else:u.emu_stop()
    elif a in [ret,base+at+5]:u.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+at,0,count=1000)
   expected_a=0x5a if label=='receive' else 1 if label=='selected' else 123
   assert seen==[[op,expected_a,regs[UC_X86_REG_EDX],789]],(label,seen)
   assert len(oldseen)==(0 if handled else 1),(label,oldseen)
   for reg,value in regs.items():
    expected=1 if label=='selected' and reg==UC_X86_REG_EAX else sp+4 if handled and reg==UC_X86_REG_ESP else value
    assert u.reg_read(reg)==expected,(label,reg,u.reg_read(reg),expected)
   checks+=1
before=pefile.PE(str(R/'analysis/single138/SAIV_IT_Runtime.exe'));after=pefile.PE(str(R/'analysis/single139/SAIV_IT_Runtime.exe'))
for rva,size in [(0x10a000,0x3000),(0x297000,0x900),(0x292000,1624),(0x2e4000,1000)]:
 assert before.get_data(rva,size)==after.get_data(rva,size),hex(rva);checks+=1
result=dict(passed=checks,normal_and_relocated=True,preserved_registers_stack_and_fallthrough=True,formula_uart_refresh_code_unchanged=True)
(R/'analysis/settings139_hook_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
