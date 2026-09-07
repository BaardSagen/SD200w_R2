from pathlib import Path
import hashlib,json,struct,subprocess,pefile
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_Detect_Priority.exe'
out=ROOT/'SD200W_SAIV_OSU107_Detect_Rows.exe'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='09a30d550aa3880e52e7b86ffc616f25e96f7eb9498d0adb47038d8d799e9911'
p=pefile.PE(data=original);b=bytearray(original)
# Retire whole-list recoloring; restore the two original calls.
for va,target in [(0x511584,0x461250),(0x51166c,0x4f3050)]:
 off=p.get_offset_from_rva(va-0x400000)
 assert b[off]==0xe8
 old_target=va+5+struct.unpack_from('<i',b,off+1)[0]
 assert 0x640000<=old_target<0x641000
 b[off:off+5]=b'\xe8'+struct.pack('<i',target-va-5)
subprocess.run(['as','--32','-o',str(W/'detect_rows.o'),str(W/'detect_rows.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'detect_rows.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'detect_rows.o'),str(W/'detect_rows.bin')],check=True)
payload=(W/'detect_rows.bin').read_bytes();rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x241000
off=p.get_offset_from_rva(0xf2695);assert b[off:off+5]==bytes.fromhex('8bd78b460c')
b[off:off+5]=b'\xe9'+struct.pack('<i',rva-0xf2695-5)
def align(n,a):return (n+a-1)//a*a
header=p.sections[-1].get_file_offset()+40
assert header+40<=p.OPTIONAL_HEADER.SizeOfHeaders and b[header:header+40]==bytes(40)
raw=align(len(b),p.OPTIONAL_HEADER.FileAlignment);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<8sIIIIIIHHI',b,header,b'.rows',len(payload),rva,size,raw,0,0,0,0,0x60000020)
struct.pack_into('<H',b,p.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(p.sections)+1)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
report=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,behavior='Recognized SD200 row: light green and black text, including when selected. Other rows retain original colors.')
(W/'detect_rows_manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
