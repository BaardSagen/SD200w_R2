"""Execute selection hooks and real instrument classifier in x86 emulator."""
from pathlib import Path
import sys,json,struct,hashlib
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'analysis/python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
m=json.loads((R/'analysis/sd200_selection_g_manifest.json').read_text());results=[]
for base in [0x400000,0x1400000]:
 for scenario in ['sd200','osu107','surface','unknown','partial','cancel','unselected','searching','not_found','open_failed','sd_unselected_osu_selected','repeat_open']:
  p=pefile.PE(str(R/m['output']));p.relocate_image(base);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x100000)
  def put(a,v):u.mem_write(a,struct.pack('<I',v))
  def get(a):return int.from_bytes(u.mem_read(a,4),'little')
  def string(a,s):b=s.encode();put(a-4,len(b));u.mem_write(a,b+b'\0');return a
  form=0x10001000;array=0x10002000;worker=0x10003000;comm=0x10004000;vmt=0x10005000;stack=0x1000f000;frame=0x1000e000;stop=0x10010000;modal=0x10010100;sleep=0x10010200
  put(base+0x1b1e1c,0x10000020);put(0x10000020,form);put(form+0x330,array);put(array-4,1);put(array,worker);put(array+16,string(0x10006000,'Instr' if scenario!='unselected' else ''))
  u.mem_write(worker+0x60,b'\1' if scenario=='searching' else b'\0');u.mem_write(worker+0x62,b'\0' if scenario=='not_found' else b'\1');u.mem_write(worker+0x71,b'\2')
  texts={'osu107':'OSU107 Instrument logger SN107','surface':'SAIV110 Surface logger','unknown':'Other device','partial':'Menu: Start via key-board <R>'}
  text=texts.get(scenario,'Menu: Start via key-board <R> Exit (passive) <H>')
  if scenario=='sd_unselected_osu_selected':text=texts['osu107'];put(array-4,2);put(array+20,0x10008000);put(array+36,string(0x10007000,''));put(0x10008000+0x5c,string(0x10009000,'Menu: Start via key-board <R> Exit (passive) <H>'))
  put(worker+0x5c,string(0x1000a000,text));put(vmt+0xd8,modal);put(base+0x1c9358,sleep);u.mem_write(frame-3,b'\1');sent=[];elapsed=[0]
  def ret(n=0):sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4+n)
  def hook(u,a,n,data):
   if a==stop:u.emu_stop()
   elif a==modal:u.reg_write(UC_X86_REG_EIP,base+m['rva']+m['symbols']['capture_close'])
   elif a==base+0x111921:
    # Original FormClose frees workers before ShowModal returns.
    u.mem_write(worker,bytes(0x80));bp=u.reg_read(UC_X86_REG_EBP);u.reg_write(UC_X86_REG_EBP,get(bp));u.reg_write(UC_X86_REG_ESP,bp+4)
    u.reg_write(UC_X86_REG_EAX,2 if scenario=='cancel' else 1);ret()
   elif a==base+0x7e8f8:u.mem_write(comm+0x24,b'\0' if scenario=='open_failed' else b'\1');u.reg_write(UC_X86_REG_EAX,0 if scenario=='open_failed' else 1);ret()
   elif a==sleep:elapsed[0]+=get(u.reg_read(UC_X86_REG_ESP)+4);ret(4)
   elif a==base+0x7ffc4:
    assert u.reg_read(UC_X86_REG_EAX)==comm and elapsed[0]>=1100
    ptr=u.reg_read(UC_X86_REG_EDX);sent.append(bytes(u.mem_read(ptr,get(ptr-4))).decode());ret()
  for a in [stop,modal,sleep,base+0x7e8f8,base+0x7ffc4,base+0x111921]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  def run(label,eax,edx=0):
   put(stack,stop)
   for reg,v in [(UC_X86_REG_EAX,eax),(UC_X86_REG_EDX,edx),(UC_X86_REG_EBX,0x1234),(UC_X86_REG_ESI,0x2345),(UC_X86_REG_EDI,0x3456),(UC_X86_REG_EBP,frame),(UC_X86_REG_ESP,stack)]:u.reg_write(reg,v)
   u.emu_start(base+m['rva']+m['symbols'][label],stop,count=100000)
   assert u.reg_read(UC_X86_REG_EIP)==stop and u.reg_read(UC_X86_REG_ESP)==stack+4
   for reg,v in [(UC_X86_REG_EBX,0x1234),(UC_X86_REG_ESI,0x2345),(UC_X86_REG_EDI,0x3456),(UC_X86_REG_EBP,frame)]:assert u.reg_read(reg)==v
  run('after_modal',form,vmt);assert u.reg_read(UC_X86_REG_EAX)==(2 if scenario=='cancel' else 1)
  assert bytes(u.mem_read(frame-1,1))==(b'\1' if scenario in ['sd200','repeat_open','open_failed'] else b'\0')
  run('reopen',comm)
  if scenario=='repeat_open':run('reopen',comm)
  assert sent==(['G'] if scenario in ['sd200','repeat_open'] else []),(scenario,sent)
  assert bytes(u.mem_read(frame-3,1))==b'\0'
  results.append(dict(base=hex(base),scenario=scenario,tx=sent))
(R/'analysis/sd200_selection_g_validation.json').write_text(json.dumps(dict(result='PASS',cases=len(results),sha256=hashlib.sha256((R/m['output']).read_bytes()).hexdigest(),details=results),indent=2))
print('PASS',len(results),'selection/identity/port-open/one-shot/register/relocation cases')
