"""Execute the Detect bridge for accept/cancel, normal Setup and relocated images."""
from pathlib import Path
import json, struct, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'analysis'/'python_packages'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *
manifest=json.loads((ROOT/'analysis'/'terminal_detect_manifest.json').read_text())
reports=[]
for base in (0x400000,0x1400000):
 for mode in ('normal','cancel','accept'):
  p=pefile.PE(str(ROOT/manifest['output']))
  if base!=p.OPTIONAL_HEADER.ImageBase:p.relocate_image(base)
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage)
  u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x10000)
  setup=0x10001000;dialog=0x10002000;vmt=0x10003000;stack=0x10008000;stop=0x10009000
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  put(setup,vmt);put(vmt+0xd8,0x10004000)
  put(setup+0x2d8,0x1234);put(setup+0x2d0,0x5678)
  put(base+0x1b1e1c,0x10005000);put(0x10005000,dialog)
  put(stack,stop)
  for reg,val in ((UC_X86_REG_EAX,setup),(UC_X86_REG_EDX,vmt),(UC_X86_REG_ESP,stack),(UC_X86_REG_EBX,0xabc),(UC_X86_REG_EDI,0xdef)):
   u.reg_write(reg,val)
  flag=base+manifest['rva']+manifest['symbols']['direct']
  u.mem_write(flag,bytes([mode!='normal']))
  calls=[]
  def ret():
   sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4)
  def hook(uc,a,size,data):
   if a==stop:u.emu_stop();return
   labels={base+0x1131bc:'initialize',base+0x116224:'detect',base+0x113c0c:'commit',0x10004000:'normal_modal'}
   if a not in labels:return
   label=labels[a];calls.append(label)
   assert u.reg_read(UC_X86_REG_EAX)==setup
   if label=='detect':
    assert u.reg_read(UC_X86_REG_EDX)==0x1234
    put(dialog+0x234,1 if mode=='accept' else 2)
   if label=='commit':assert u.reg_read(UC_X86_REG_EDX)==0x5678
   u.reg_write(UC_X86_REG_EAX,2);ret()
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(base+manifest['rva']+manifest['symbols']['modal_bridge'],stop,count=1000)
  assert calls==({'normal':['normal_modal'],'cancel':['initialize','detect'],'accept':['initialize','detect','commit']}[mode])
  assert u.reg_read(UC_X86_REG_EAX)==(1 if mode=='accept' else 2)
  assert u.reg_read(UC_X86_REG_EBX)==0xabc and u.reg_read(UC_X86_REG_EDI)==0xdef
  assert u.reg_read(UC_X86_REG_ESP)==stack+4 and bytes(u.mem_read(flag,1))==b'\0'
  reports.append(dict(base=hex(base),mode=mode,calls=calls))
(ROOT/'analysis'/'terminal_detect_validation.json').write_text(json.dumps(dict(result='PASS',cases=reports),indent=2))
print('PASS: accept, cancel and normal Setup; stack/register preservation; both image bases.')
