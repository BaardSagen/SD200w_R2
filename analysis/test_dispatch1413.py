"""Exercise the shipped common click route at normal and relocated bases."""
from pathlib import Path
import json,sys,struct,pefile
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parent.parent
manifest=json.loads((R/'analysis/single1413_settings/dispatch_manifest.json').read_text())
checks=[]
for base in (0x400000,0x1400000):
 p=pefile.PE(str(R/'analysis/single1413_settings/SAIV_IT_Runtime.exe'));p.relocate_image(base)
 for name,tag in [('null',None),('Convert',0),('Interval',0x53495449),('TIME/DATE',0x53495454),('Merge',0x534d4752),('other tagged action',123)]:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,bytes(p.get_memory_mapped_image()))
  u.mem_map(0x10000000,0x20000);sender=0x10002000 if tag is not None else 0
  if sender:u.mem_write(sender+12,struct.pack('<I',tag))
  regs={UC_X86_REG_EAX:0x10001000,UC_X86_REG_EDX:sender,UC_X86_REG_ECX:12,UC_X86_REG_EBX:13,UC_X86_REG_ESI:14,UC_X86_REG_EDI:15,UC_X86_REG_EBP:16,UC_X86_REG_ESP:0x10010000}
  for reg,value in regs.items():u.reg_write(reg,value)
  seen=[]
  def hook(engine,at,size,arg):
   if at in [base+manifest['legacy_rva'],base+manifest['batch_rva']]:seen.append(at);engine.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+manifest['entry_rva'],0,count=30)
  expected=manifest['batch_rva'] if tag in (None,0) else manifest['legacy_rva']
  assert seen==[base+expected],(name,seen,expected)
  assert all(u.reg_read(reg)==value for reg,value in regs.items()),name
  checks.append(dict(base=base,action=name,correct_route=True,registers_and_stack_preserved=True))
report=dict(passed=True,checks=checks)
(R/'analysis/dispatch1413_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS',len(checks),'dispatch scenarios, normal/relocated, registers and stack preserved')
