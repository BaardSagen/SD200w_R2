"""Test the actual x86 soft parity hooks; no physical serial ports."""
from pathlib import Path
import sys,struct,json,hashlib
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'analysis/python_packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
m=json.loads((R/'analysis/soft_parity_manifest.json').read_text());results=[]
for base in (0x400000,0x1400000):
 p=pefile.PE(str(R/m['output']));p.relocate_image(base);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage);u.mem_write(base,bytes(p.get_memory_mapped_image()));u.mem_map(0x10000000,0x100000)
 stack=0x10008000;frame=0x10007000;obj=0x10001000;stop=0x10009000;dcb=0x10002000;buf=0x10003000;out=0x10004000;local=0x10005000;source=0x10006008;copy=0x1000b008
 calls=[];read_success=1;read_bytes=256;captured=[]
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def ret(n=0):sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4+n)
 def hook(u,a,size,data):
  sp=u.reg_read(UC_X86_REG_ESP)
  if a==stop:u.emu_stop()
  elif a==base+0x7b5c:
   assert get(sp+4)==123;captured.append(bytes(u.mem_read(get(sp+8),28)));u.reg_write(UC_X86_REG_EAX,1);ret(8)
  elif a==base+0x7b4c:
   assert [get(sp+i) for i in (4,8,12,16,20)]==[123,buf,256,out,0]
   put(out,read_bytes);u.reg_write(UC_X86_REG_EAX,read_success);ret(20)
  elif a==base+0x405c:
   length=u.reg_read(UC_X86_REG_EAX);put(copy-8,1);put(copy-4,length);u.mem_write(copy+length,b'\0');u.reg_write(UC_X86_REG_EAX,copy);calls.append('allocate');ret()
  elif a==base+0x2a24:
   src=u.reg_read(UC_X86_REG_EAX);dst=u.reg_read(UC_X86_REG_EDX);length=u.reg_read(UC_X86_REG_ECX);u.mem_write(dst,bytes(u.mem_read(src,length)));calls.append('copy');ret()
 for a in [stop]+[base+x for x in (0x7b5c,0x7b4c,0x405c,0x2a24)]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
 def run(name,args=(),eax=0):
  put(stack,stop)
  for i,a in enumerate(args):put(stack+4+i*4,a)
  for reg,val in [(UC_X86_REG_ESP,stack),(UC_X86_REG_EBP,frame),(UC_X86_REG_EBX,0x123456),(UC_X86_REG_ESI,0x234567),(UC_X86_REG_EDI,obj),(UC_X86_REG_EAX,eax)]:u.reg_write(reg,val)
  u.emu_start(base+m['rva']+m['symbols'][name],stop,count=100000)
  assert u.reg_read(UC_X86_REG_EIP)==stop
  assert u.reg_read(UC_X86_REG_ESP)==stack+4+len(args)*4
  assert u.reg_read(UC_X86_REG_EBP)==frame and u.reg_read(UC_X86_REG_EBX)==0x123456 and u.reg_read(UC_X86_REG_ESI)==0x234567 and u.reg_read(UC_X86_REG_EDI)==obj
  return u.reg_read(UC_X86_REG_EAX)
 for bits,parity in [(7,2),(8,0),(8,2),(7,1)]:
  original=bytearray(range(28));struct.pack_into('<II',original,0,28,9600);struct.pack_into('<I',original,8,0x3fff);original[24]=bits;original[25]=parity;original[26]=0;u.mem_write(dcb,bytes(original));assert run('configure',[123,dcb])==1
  expected=bytearray(original);struct.pack_into('<I',expected,8,0x3fff&~0x4c)
  if (bits,parity)==(7,2):expected[24]=8;expected[25]=0;struct.pack_into('<I',expected,8,get(dcb+8)&~0x4e)
  assert captured[-1]==expected,(bits,parity,captured[-1],expected)
  assert bytes(u.mem_read(dcb,28))==original,'logical DCB changed'
  results.append(dict(base=hex(base),test='DCB',bits=bits,parity=parity))
 payload=bytes(range(256));put(frame-4,obj)
 for parity,bits in [('e',7),('n',8),('e',8)]:
  u.mem_write(obj+0x4c,bytes([ord(parity),bits]));put(source-8,2);put(source-4,256);u.mem_write(source,payload+b'\0');put(local,source);calls.clear();ptr=run('send_string',eax=local)
  assert ptr==copy and calls==['allocate','copy'],'must use real Delphi copy-on-write'
  expected=bytes((v&127)|(((v&127).bit_count()%2)<<7) for v in payload) if (parity,bits)==('e',7) else payload
  assert bytes(u.mem_read(ptr,256))==expected
  assert bytes(u.mem_read(source,256))==payload and get(source-8)==1,'shared original modified'
  assert get(ptr-4)==256
  results.append(dict(base=hex(base),test='send_all_256',parity=parity,bits=bits))
  for success,count in [(1,256),(1,0),(0,256),(1,257)]:
   read_success=success;read_bytes=count;u.mem_write(buf,payload+b'GUARD');assert run('receive',[123,buf,256,out,0])==success
   expected=bytes(v&127 for v in payload) if (parity,bits)==('e',7) and success and count==256 else payload
   assert bytes(u.mem_read(buf,261))==expected+b'GUARD'
   results.append(dict(base=hex(base),test='receive_all_256',parity=parity,bits=bits,success=success,count=count))
 # Nil string stays nil and never dereferences its header.
 put(local,0);assert run('send_string',eax=local)==0
report=dict(result='PASS',exe=m['output'],sha256=hashlib.sha256((R/m['output']).read_bytes()).hexdigest(),cases=len(results),details=results)
(R/'analysis/soft_parity_validation.json').write_text(json.dumps(report,indent=2));print('PASS',len(results),'x86 hook scenarios; all byte values, DCB preservation, real copy-on-write, error/empty reads and relocation')
