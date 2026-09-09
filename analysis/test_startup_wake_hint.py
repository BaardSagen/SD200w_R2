from pathlib import Path
import sys,json,struct,hashlib
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'analysis/python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
m=json.loads((R/'analysis/startup_wake_hint_manifest.json').read_text());results=[]
for base in [0x400000,0x1400000]:
 for scenario in ['silent','early_rx','late_rx','changed_port','closed_form','timer_failed','repeat_start']:
  p=pefile.PE(str(R/m['output']));p.relocate_image(base);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x100000)
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return int.from_bytes(u.mem_read(a,4),'little')
  form=0x10001000;comm=0x10003000;control=0x10004000;vmt=0x10005000;stack=0x10008000;stop=0x10009000;timer=0x1000a000;kill=0x1000a010;paint=0x1000a020
  put(base+0x1c8964,form);put(form+0x510,comm);u.mem_write(comm+0x34,b'\7');put(form+0x44c,control);put(control,vmt);put(vmt+0x74,paint);put(base+0x1c9708,timer);put(base+0x1c97c4,kill);calls=[];lines=[]
  def ret(n=0):sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4+n)
  def hook(u,a,n,d):
   if a==stop:u.emu_stop()
   elif a==timer:
    assert get(u.reg_read(UC_X86_REG_ESP)+12)==3000;calls.append('schedule');u.reg_write(UC_X86_REG_EAX,0 if scenario=='timer_failed' else 123);ret(16)
   elif a==kill:calls.append('kill');ret(8)
   elif a==base+0x1a0ff0:calls.append('open_terminal');ret()
   elif a==base+0x19bbd4:
    assert u.reg_read(UC_X86_REG_EAX)==form;ptr=u.reg_read(UC_X86_REG_EDX);lines.append(bytes(u.mem_read(ptr,get(ptr-4))).decode());ret()
   elif a==paint:ret()
   elif a==base+0x292000:ret()
   else:raise AssertionError('Serial TX must not be called')
  for a in [stop,timer,kill,paint,base+0x1a0ff0,base+0x19bbd4,base+0x292000,base+0x7ffc4]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  def run(label):
   put(stack,stop)
   for i,v in enumerate([0,0,123,3000]):put(stack+4+i*4,v)
   for reg,v in [(UC_X86_REG_ESP,stack),(UC_X86_REG_EBP,0x1000b000),(UC_X86_REG_EBX,12),(UC_X86_REG_ESI,13),(UC_X86_REG_EDI,14)]:u.reg_write(reg,v)
   u.emu_start(base+m['rva']+m['symbols'][label],stop,count=10000)
   assert u.reg_read(UC_X86_REG_EIP)==stop
   assert u.reg_read(UC_X86_REG_ESP)==stack+(20 if label=='timer_callback' else 4)
   for reg,v in [(UC_X86_REG_EBP,0x1000b000),(UC_X86_REG_EBX,12),(UC_X86_REG_ESI,13),(UC_X86_REG_EDI,14)]:assert u.reg_read(reg)==v
  if scenario=='early_rx':run('receive')
  run('start')
  if scenario=='repeat_start':run('start')
  if scenario=='late_rx':run('receive')
  if scenario=='changed_port':u.mem_write(comm+0x34,b'\x0b')
  if scenario=='closed_form':put(base+0x1c8964,0)
  run('timer_callback');run('timer_callback')
  expected=['Hold <I> to wake the instrument, or use Detect to find connected units.'] if scenario in ['silent','repeat_start'] else []
  assert lines==expected,(scenario,lines);assert calls.count('schedule')==1
  results.append(dict(base=hex(base),scenario=scenario,lines=lines))
(R/'analysis/startup_wake_hint_validation.json').write_text(json.dumps(dict(result='PASS',cases=len(results),sha256=hashlib.sha256((R/m['output']).read_bytes()).hexdigest(),details=results),indent=2))
print('PASS',len(results),'startup silence, RX, one-shot, port/lifetime and relocation cases; no serial TX')
