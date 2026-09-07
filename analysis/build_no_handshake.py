from pathlib import Path
import hashlib,json,struct,pefile
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'SD200W_SAIV_OSU107_RefreshReply_EN.exe';out=ROOT/'SD200W_SAIV_OSU107_NoHandshake.exe'
b=bytearray(source.read_bytes());assert hashlib.sha256(b).hexdigest()=='4ff9fa8c1b464ffb38c1839d5d457bbbee87cf17eea48ff4b0934781dd8f2c45'
p=pefile.PE(data=bytes(b));rva=p.OPTIONAL_HEADER.SizeOfImage
# stdcall SetCommState(handle, DCB*): clear fOutxCtsFlow, fOutxDsrFlow, fDsrSensitivity.
# Preserve DTR/RTS settings, software flow control, baud, parity and word length.
payload=bytes.fromhex('508b44240c816008b3ffffff58')
payload+=b'\xe9'+struct.pack('<i',0x7b5c-rva-len(payload)-5)
for va in (0x47e6b2,0x47e87a,0x47e8ee,0x47f427):
 off=p.get_offset_from_rva(va-0x400000);assert b[off]==0xe8
 assert va+5+struct.unpack_from('<i',b,off+1)[0]==0x407b5c
 b[off:off+5]=b'\xe8'+struct.pack('<i',rva+0x400000-va-5)
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
m=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,flags_cleared='fOutxCtsFlow, fOutxDsrFlow, fDsrSensitivity')
(ROOT/'analysis/no_handshake_manifest.json').write_text(json.dumps(m,indent=2));print(m)
