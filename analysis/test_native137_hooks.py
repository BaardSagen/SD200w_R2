"""Execute each native bridge gate at original/relocated image bases."""
from pathlib import Path
import sys,json,struct
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
R=Path(__file__).resolve().parent.parent;m=json.loads((R/'analysis/native137_manifest.json').read_text());checks=0
for base in [0x400000,0x1400000]:
 for at,label,op,n in m['patches']:
  if op is None:continue
  p=pefile.PE(str(R/'analysis/single137/SAIV_IT_Runtime.exe'));p.relocate_image(base);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x20000)
  ret=0x1001f000;callback=0x1001e000;sp=0x10010000;args=[]
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return int.from_bytes(u.mem_read(a,4),'little')
  put(base+m['rva']+m['symbols']['entry_ptr'],callback);put(sp,ret);put(sp+4,987)
  regs={UC_X86_REG_EAX:123,UC_X86_REG_EDX:456,UC_X86_REG_ECX:789,UC_X86_REG_EBX:111,UC_X86_REG_EDI:222,UC_X86_REG_ESI:333,UC_X86_REG_EBP:0x10008000,UC_X86_REG_ESP:sp,UC_X86_REG_EFLAGS:0x246}
  for r,v in regs.items():u.reg_write(r,v)
  def hook(u,a,n,d):
   if a==ret:u.emu_stop()
   elif a==callback:
    stack=u.reg_read(UC_X86_REG_ESP);args.append([get(stack+i) for i in [4,8,12,16]]);u.reg_write(UC_X86_REG_EIP,get(stack));u.reg_write(UC_X86_REG_ESP,stack+20)
    for r in [UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX]:u.reg_write(r,0xdeadbeef)
    u.reg_write(UC_X86_REG_EAX,1)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+at,0,count=1000);assert u.reg_read(UC_X86_REG_EIP)==ret,label;assert args==[[op,123,456,789]],(label,args)
  assert all(u.reg_read(r)==v for r,v in regs.items() if r!=UC_X86_REG_ESP),label;assert u.reg_read(UC_X86_REG_ESP)==sp+4+(4 if label=='fill' else 0),label;checks+=1
# Retain the delivered native calculation, UART and Download code.
a=pefile.PE(str(R/'analysis/single136/SAIV_IT_Runtime.exe'));b=pefile.PE(str(R/'analysis/single137/SAIV_IT_Runtime.exe'))
for at,size in [(0x10a000,0x3000),(0x297000,0x900),(0x292000,1624),(0x1a14f4,0xd3),(0x1496aa,5)]:assert a.get_data(at,size)==b.get_data(at,size),hex(at);checks+=1
(R/'analysis/native137_hook_validation.json').write_text(json.dumps(dict(passed=checks,normal_and_relocated=True,native_calculations_uart_download_unchanged=True),indent=2));print('PASS',checks,'bridge register/stack/ASLR and unchanged calculation/UART/Download checks')
