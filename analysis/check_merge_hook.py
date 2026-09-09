"""Verify Delphi Merge event dispatch, stack preservation, cache and ASLR."""
from pathlib import Path
import sys,struct,json
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parent.parent
p=pefile.PE(str(ROOT/'SAIV_Instrument_Terminal_v1.3.0_Sept2026.exe'))
results=[]
for base in [0x400000,0x10000000]:
 for mode in ['merge','cached','import','null_sender','missing_dll','missing_export','long_path']:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,0x400000);u.mem_write(base,p.get_memory_mapped_image())
  u.mem_map(0x20000000,0x10000);u.mem_map(0x21000000,0x10000);u.mem_map(0x22000000,0x1000)
  sp=0x20008000;obj=0x21000100;sender=0x21001000
  def w32(a,v):u.mem_write(a,struct.pack('<I',v))
  def r32(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def z(a):return bytes(u.mem_read(a,260)).split(b'\0',1)[0]
  w32(obj+0x14c,1234);w32(sender+12,0 if mode=='import' else 0x534d4752)
  for off,addr in [(0x1c9228,0x22000010),(0x1c9214,0x22000020),(0x1c9220,0x22000030),(0x1c97a0,0x22000040)]:w32(base+off,addr)
  registers={UC_X86_REG_EAX:obj,UC_X86_REG_EBX:0xabc,UC_X86_REG_ECX:0xdef,UC_X86_REG_EDX:0 if mode=='null_sender' else sender,UC_X86_REG_ESI:0x123,UC_X86_REG_EDI:0x456,UC_X86_REG_EBP:0x789,UC_X86_REG_ESP:sp}
  calls=[];targets=[]
  def hook(uc,addr,size,data):
   if addr in [base+0x1a5944,0x22000080]:targets.append(addr);uc.emu_stop();return
   if not 0x22000000<=addr<0x22001000:return
   stack=uc.reg_read(UC_X86_REG_ESP);args=[r32(stack+4+i*4) for i in range(4)];calls.append(addr)
   if addr==0x22000010:
    path=b'C:\\SIT\\terminal.exe\0';uc.mem_write(args[1],path);ret=259 if mode=='long_path' else len(path)-1;n=3
   elif addr==0x22000020:
    assert z(args[0])==b'C:\\SIT\\SIT_Import130.dll';assert args[1:3]==[0,8];ret=0 if mode=='missing_dll' else 7;n=3
   elif addr==0x22000030:
    assert z(args[1])==b'SitMerge';ret=0 if mode=='missing_export' else 0x22000050;n=2
   elif addr==0x22000040:assert args[0]==1234;ret=1;n=4
   else:assert addr==0x22000050 and args[0]==1234;ret=1;n=1
   uc.reg_write(UC_X86_REG_EAX,ret);uc.reg_write(UC_X86_REG_ESP,stack+4+n*4);uc.reg_write(UC_X86_REG_EIP,r32(stack))
  u.hook_add(UC_HOOK_CODE,hook)
  for iteration in range(2 if mode=='cached' else 1):
   calls.clear();targets.clear();w32(sp,0x22000080)
   for reg,v in registers.items():u.reg_write(reg,v)
   u.emu_start(base+0x1a593c,base+0x3fffff,count=3000)
   ordinary=mode in ['import','null_sender'];assert targets==[base+0x1a5944 if ordinary else 0x22000080]
   for reg,v in registers.items():
    expected=sp-4 if ordinary and reg in [UC_X86_REG_ESP,UC_X86_REG_EBP] else 6 if ordinary and reg==UC_X86_REG_ECX else sp+4 if reg==UC_X86_REG_ESP else v
    assert u.reg_read(reg)==expected,(mode,reg,hex(u.reg_read(reg)),hex(expected))
   if ordinary:assert not calls and r32(sp-4)==registers[UC_X86_REG_EBP]
   if mode=='cached' and iteration==1:assert calls==[0x22000050]
   results.append(dict(base=hex(base),mode=mode,iteration=iteration,passed=True))
(ROOT/'analysis/runtime_test/merge130/hook_validation.json').write_text(json.dumps(results,indent=2))
print('PASS',len(results),'Merge dispatch/stack/register/relocation/cache checks')
