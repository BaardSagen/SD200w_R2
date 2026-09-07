from pathlib import Path
import pefile,json,struct,sys
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
p=pefile.PE('SD200W_SAIV_OSU107_NoHandshake.exe');rva=json.loads(Path('analysis/no_handshake_manifest.json').read_text())['rva'];code=p.get_data(rva,18)
n=0
for base in (0x400000,0x10000000):
 for flags in (0,0x1011,0xffffffff,0x4c,0x1311):
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,0x300000);u.mem_write(base+rva,code)
  u.mem_map(0x20000000,0x2000);stack=0x20001000;dcb=0x20000040
  u.mem_write(stack,struct.pack('<III',0x12345678,123,dcb));u.mem_write(dcb,bytes(range(28)));u.mem_write(dcb+8,struct.pack('<I',flags))
  before=bytes(u.mem_read(dcb,28));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EAX,0xabcdef)
  u.emu_start(base+rva,base+0x7b5c,count=10)
  assert u.reg_read(UC_X86_REG_EIP)==base+0x7b5c
  assert u.reg_read(UC_X86_REG_ESP)==stack and u.reg_read(UC_X86_REG_EAX)==0xabcdef
  after=bytes(u.mem_read(dcb,28));assert after[:8]==before[:8] and after[12:]==before[12:]
  assert struct.unpack_from('<I',after,8)[0]==flags&0xffffffb3
  n+=1
for va in (0x47e6b2,0x47e87a,0x47e8ee,0x47f427):
 b=p.get_data(va-0x400000,5);assert b[0]==0xe8 and va+5+struct.unpack_from('<i',b,1)[0]==0x400000+rva
assert p.verify_checksum()
print(f'PASS: {n} flag/rebase cases, four call sites, preserved registers/stack/DCB, PE checksum')


