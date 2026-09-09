"""Create diagnostic-only copy allowing COM7; never ship this as the product."""
from pathlib import Path
import pefile,struct,hashlib,json,sys
R=Path(__file__).resolve().parent.parent;source=R/'SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe';b=bytearray(source.read_bytes());p=pefile.PE(data=b);rva=p.OPTIONAL_HEADER.SizeOfImage
payload=bytes.fromhex('80783407740333c0c3')+b'\xe9'+struct.pack('<i',0x2831a0-rva-14)
off=p.get_offset_from_rva(0x1039b2);assert 0x1039b7+struct.unpack_from('<i',b,off+1)[0]==0x2831a0;b[off:off+5]=b'\xe8'+struct.pack('<i',rva-0x1039b7)
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment);b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload));struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment));struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=b).generate_checksum())
sys.path.insert(0,str(R/'analysis/python_packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
for port in [7,11,18]:
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x300000);u.mem_write(0x400000+rva,payload);u.mem_map(0x10000000,0x10000);u.mem_write(0x10000034,bytes([port]));u.mem_write(0x10008000,struct.pack('<I',0x10009000));u.reg_write(UC_X86_REG_EAX,0x10000000);u.reg_write(UC_X86_REG_ESP,0x10008000);end=0x6831a0 if port==7 else 0x10009000;u.emu_start(0x400000+rva,end,count=20);assert u.reg_read(UC_X86_REG_EIP)==end
out=R/'analysis/runtime_test/COM7_SELECT_G_DIAGNOSTIC.exe';out.write_bytes(b);assert pefile.PE(data=b).verify_checksum()
(R/'analysis/com7_select_g_diagnostic_manifest.json').write_text(json.dumps(dict(source=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),diagnostic_sha256=hashlib.sha256(b).hexdigest(),scope='Only COM7 can open; gate verified by x86 emulator; product probe unchanged'),indent=2))
print('PASS COM7-only diagnostic built and guard tested')
