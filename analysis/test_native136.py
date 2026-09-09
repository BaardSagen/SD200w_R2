"""Execute real native136 code with isolated memory; never opens serial ports."""
from pathlib import Path
import sys,json,struct
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
R=Path(__file__).resolve().parent.parent;m=json.loads((R/'analysis/native136_manifest.json').read_text());checks=[]
class H:
 def __init__(self,base):
  self.base=base;p=pefile.PE(str(R/'analysis/single136/SAIV_IT_Runtime.exe'));p.relocate_image(base);self.u=Uc(UC_ARCH_X86,UC_MODE_32);self.u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);self.u.mem_write(base,bytes(p.get_memory_mapped_image()));self.u.mem_map(0x10000000,0x40000);self.form=0x10001000;self.comm=0x10006000;self.dlg=0x1000c000;self.ret=0x1003f000;self.sp=0x10030000
  self.put(self.form+0x374,123);self.put(self.form+0x510,self.comm);self.byte(self.comm+0x34,7);self.u.hook_add(UC_HOOK_CODE,self.hook)
 def a(self,n):return self.base+m['rva']+m['symbols'][n]
 def constant(self,n):return self.base+m['constants'][n]
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def byte(self,a,v=None):
  if v is not None:self.u.mem_write(a,bytes([v]))
  return self.u.mem_read(a,1)[0]
 def state(self,n,v=None):return self.byte(self.a(n),v)
 def hook(self,u,a,n,d):
  if a in self.stops:u.emu_stop()
  elif a==self.constant('OLD_SELECTED'):
   sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,int.from_bytes(u.mem_read(sp,4),'little'));u.reg_write(UC_X86_REG_ESP,sp+4)
 def run(self,label,stops,eax=0,edx=0,ebx=0):
  self.stops=set(stops)|{self.ret};self.put(self.sp,self.ret)
  for r,v in [(UC_X86_REG_EAX,eax),(UC_X86_REG_EDX,edx),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESP,self.sp),(UC_X86_REG_EBP,0x1002f000),(UC_X86_REG_EDI,0x12345678),(UC_X86_REG_EFLAGS,0x246)]:self.u.reg_write(r,v)
  self.u.emu_start(self.a(label),0,count=10000);where=self.u.reg_read(UC_X86_REG_EIP);assert where in self.stops,(label,hex(where));return where
for base in (0x400000,0x1400000):
 for kind,port,actual,tcp,known,sender,expected in [(1,7,7,0,0,123,1),(2,7,7,0,0,123,1),(1,7,11,0,0,123,0),(0,7,7,0,0,123,0),(1,7,7,1,0,123,0),(1,7,7,0,0,124,0),(0,0,7,0,1,123,1),(1,0,7,0,0,123,0)]:
  h=H(base);h.state('confirmed_type',kind);h.state('confirmed_port',port);h.byte(h.comm+0x34,actual);h.byte(h.comm+0x407e,tcp);h.byte(h.constant('LOGGER_KNOWN'),known);h.run('download',[h.constant('OLD_DOWNLOAD')],h.form,sender);assert h.state('logger_active')==expected;assert h.u.reg_read(UC_X86_REG_EAX)==h.form and h.u.reg_read(UC_X86_REG_EDX)==sender and h.u.reg_read(UC_X86_REG_EDI)==0x12345678;checks.append('download identity/port/Log/TCP')
 for response,result in [('OSU107 instrument logger',1),('SAIV110 surface logger',2),('unrecognized',0)]:
  h=H(base);rows=0x10012000;worker=0x10013000;action=0x10014004;banner=0x10015000;h.put(h.form+0x330,rows);h.put(rows-4,1);h.put(rows,worker);h.put(rows+16,action);h.put(action-4,5);h.u.mem_write(action,b'Instr\0');h.byte(worker+0x62,1);h.byte(worker+0x71,2);h.put(worker+0x64,h.comm);h.put(worker+0x5c,banner);h.u.mem_write(banner,response.encode()+b'\0');h.run('capture',[h.constant('OLD_CAPTURE')],h.form);assert h.state('pending_type')==result,(response,h.state('pending_type'));assert h.state('pending_port')==7
  h.state('confirmed_type',2);h.state('confirmed_port',11);h.run('selected',[],2);assert h.state('confirmed_type')==2 and h.state('confirmed_port')==11
  h.byte(h.constant('LOGGER_KNOWN'),1);h.run('selected',[],1);assert h.state('confirmed_type')==result and h.state('confirmed_port')==7 and h.byte(h.constant('LOGGER_KNOWN'))==0;checks.append('real classifier/capture/OK/Cancel')
 for active in (0,1):
  h=H(base);h.state('logger_active',active);h.byte(h.dlg+0xa67,1);where=h.run('prescan',[base+0x1518ec],h.dlg);assert where==(h.ret if active else base+0x1518ec);assert h.byte(h.dlg+0xa67)==(0 if active else 1);checks.append('stale CTD/Burst prescan')
  for requested in (0,1):
   for log in (0,1):
    h.byte(h.constant('REQUESTED'),requested);h.byte(h.dlg+0xa60,log);where=h.run('logger_line',[h.constant('OLD_LINE')],h.dlg);assert where==(h.ret if active and requested and not log else h.constant('OLD_LINE'));checks.append('CTD line parser gating')
 for ascii in (0,1):
  h=H(base);sender=0x10018000;h.put(sender+12,0x41534349 if ascii else 0);h.run('import_entry',[h.constant('OLD_IMPORT_ENTRY')],h.form,sender);assert h.state('ascii_mode')==ascii
  h.run('import_title',[base+0x1a596c]);ptr=h.u.reg_read(UC_X86_REG_EDX);length=int.from_bytes(h.u.mem_read(ptr-4,4),'little');assert bytes(h.u.mem_read(ptr,length))==(b'Import CSV/TXT' if ascii else b'Convert CSV/TXT')
  where=h.run('import_file',[base+0x1a5a53,h.constant('OLD_IMPORT_FILE')],ebx=h.form);assert where==(base+0x1a5a53 if ascii else h.constant('OLD_IMPORT_FILE'));checks.append('separate native import/Convert dispatcher and titles')
(R/'analysis/native136_validation.json').write_text(json.dumps(dict(passed=len(checks),checks=checks),indent=2));print('PASS',len(checks),'native hooks including relocated image, real classifier and parser guards')
