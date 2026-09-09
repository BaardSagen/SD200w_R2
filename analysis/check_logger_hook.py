"""Emulate import hook branches and relocation without loading a DLL or using instruments."""
from pathlib import Path
import sys,struct,json
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parent.parent;p=pefile.PE(str(ROOT/'SAIV_Instrument_Terminal_v1.2.0_Sept2026.exe'));entry=0x2d5000
results=[]
for base in [0x400000,0x10000000]:
 for mode in ['logger','legacy','missing_dll','missing_export','long_path']:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,0x400000);u.mem_write(base,p.get_memory_mapped_image());u.mem_map(0x20000000,0x10000);u.mem_map(0x21000000,0x10000);u.mem_map(0x22000000,0x1000)
  sp=0x20008000;bp=sp+0x1000;obj=0x21000100;filename=0x21002000;u.mem_write(filename,b'C:\\data\\sample.txt\0')
  def w32(a,n):u.mem_write(a,struct.pack('<I',n))
  def r32(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  w32(obj+0x14c,1234);w32(obj+0x2e8,0xabcdef);w32(bp-0x18,filename)
  for off,addr in [(0x1c9228,0x22000010),(0x1c9214,0x22000020),(0x1c9220,0x22000030),(0x1c97a0,0x22000040)]:w32(base+off,addr)
  regs={UC_X86_REG_EAX:0x123,UC_X86_REG_EBX:obj,UC_X86_REG_ECX:0x234,UC_X86_REG_EDX:0x345,UC_X86_REG_ESI:0x456,UC_X86_REG_EDI:0x567,UC_X86_REG_EBP:bp,UC_X86_REG_ESP:sp}
  for reg,value in regs.items():u.reg_write(reg,value)
  calls=[];target=[]
  def hook(uc,addr,size,data):
   if addr in [base+0x1a5b39,base+0x1a5a53]:target.append(addr);uc.emu_stop();return
   if not 0x22000000<=addr<0x22001000:return
   stack=uc.reg_read(UC_X86_REG_ESP);args=[r32(stack+4+i*4) for i in range(3)];calls.append(addr)
   if addr==0x22000010:
    path=b'C:\\SIT\\terminal.exe\0';uc.mem_write(args[1],path);ret=259 if mode=='long_path' else len(path)-1;n=3
   elif addr==0x22000020:ret=0 if mode=='missing_dll' else 7;n=3
   elif addr==0x22000030:ret=0 if mode=='missing_export' else 0x22000050;n=2
   elif addr==0x22000040:ret=1;n=4
   else:assert args[:2]==[1234,filename];ret=0 if mode=='legacy' else 1;n=2
   uc.reg_write(UC_X86_REG_EAX,ret);uc.reg_write(UC_X86_REG_ESP,stack+4+n*4);uc.reg_write(UC_X86_REG_EIP,r32(stack))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+entry,base+0x3fffff,count=2000)
  assert target==[base+(0x1a5a53 if mode=='legacy' else 0x1a5b39)],(mode,target)
  for reg,value in regs.items():
   expected=0xabcdef if mode=='legacy' and reg==UC_X86_REG_EAX else bp-0x20 if mode=='legacy' and reg==UC_X86_REG_EDX else value
   assert u.reg_read(reg)==expected,(mode,reg,hex(u.reg_read(reg)),hex(expected))
  results.append(dict(base=hex(base),mode=mode,passed=True))
(ROOT/'analysis/runtime_test/logger_hook_validation.json').write_text(json.dumps(results,indent=2));print('PASS',len(results),'hook branches/relocation/register tests')
