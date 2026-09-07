from pathlib import Path
import json,struct,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'analysis'/'python_packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
m=json.loads((ROOT/'analysis'/'detect_green_manifest.json').read_text())
cases=[[],[(1,2)],[(0,0)],[(0,1)],[(0,3)],[(0,4)],[(0,255)],[(0,2)],[(1,2),(0,3),(0,2)]]
reports=[]
for base in (0x400000,0x1400000):
 for states in cases:
  p=pefile.PE(str(ROOT/m['output']))
  if base!=0x400000:p.relocate_image(base)
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage)
  u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x10000)
  form=0x10001000;array=0x10002004;stack=0x10008000;frame=0x10009000;stop=0x1000a000
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  put(form+0x330,array if states else 0);put(array-4,len(states));put(form+0x2e4,0x123456)
  for i,(searching,kind) in enumerate(states):
   obj=0x10003000+i*0x100;put(array+i*20,obj)
   u.mem_write(obj+0x60,bytes([searching]));u.mem_write(obj+0x71,bytes([kind]))
  put(frame-4,form);put(stack,stop)
  initial={UC_X86_REG_ESP:stack,UC_X86_REG_EBP:frame,UC_X86_REG_EBX:form,UC_X86_REG_ESI:0x111,UC_X86_REG_EDI:0x222}
  for r,v in initial.items():u.reg_write(r,v)
  colors=[]
  def hook(uc,a,size,data):
   if a in (base+0x61250,base+0xf1b34):
    if a==base+0xf1b34:
     assert u.reg_read(UC_X86_REG_EAX)==0x123456
     colors.append((u.reg_read(UC_X86_REG_EDX),u.reg_read(UC_X86_REG_ECX)))
    sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4)
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(base+m['rva'],stop,count=1000)
  expected=0xd8f2d8 if (0,2) in states else 0x80000005
  assert colors==[(1,expected),(0,expected)],(states,colors)
  for r,v in initial.items():assert u.reg_read(r)==v+(4 if r==UC_X86_REG_ESP else 0)
  reports.append(dict(base=hex(base),states=states,color=hex(expected)))
(ROOT/'analysis'/'detect_green_validation.json').write_text(json.dumps(dict(result='PASS',cases=reports),indent=2))
print('PASS: 18 empty/searching/recognized/unknown/busy/error and relocated cases.')
