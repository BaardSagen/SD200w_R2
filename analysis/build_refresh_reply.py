from pathlib import Path
import hashlib,json,struct,subprocess,re,pefile
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_Clean.exe';out=ROOT/'SD200W_SAIV_OSU107_RefreshReply.exe'
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()=='6e85e29b24200ffc5c57084ab9bd51489d6a71da01b8800ac851145b420d6779'
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x292000
subprocess.run(['as','--32','-o',str(W/'refresh_reply.o'),str(W/'refresh_reply.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'refresh_reply.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'refresh_reply.o'),str(W/'refresh_reply.bin')],check=True)
payload=(W/'refresh_reply.bin').read_bytes()
symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'refresh_reply.o')],text=True).splitlines() if len(t:=line.split())==3}
prev=json.loads((W/'clean_manifest.json').read_text())
for va,label in [(0x59b308,'receive_hook'),(0x5a14f4,'click_hook'),(0x5a156f,'after_modal_hook'),(0x47f9c4,'close_port_hook')]:
 off=p.get_offset_from_rva(va-0x400000);assert b[off]==0xe9
 assert va+5+struct.unpack_from('<i',b,off+1)[0]==0x400000+prev['section_rva']+prev['symbols'][label]
 b[off:off+5]=b'\xe9'+struct.pack('<i',0x400000+rva+symbols[label]-va-5)
off=p.get_offset_from_rva(0x1496aa);assert b[off]==0xe8 and 0x1496aa+5+struct.unpack_from('<i',b,off+1)[0]==prev['section_rva']+prev['symbols']['line_hook']
b[off:off+5]=b'\xe8'+struct.pack('<i',rva+symbols['line_hook']-0x1496aa-5)
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload))
struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
m=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),section_rva=rva,section_size=len(payload),symbols=symbols)
(W/'refresh_reply_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({k:v for k,v in m.items() if k!='symbols'},indent=2))
