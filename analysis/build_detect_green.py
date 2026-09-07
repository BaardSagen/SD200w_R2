from pathlib import Path
import hashlib,json,struct,subprocess,pefile
ROOT=Path(__file__).resolve().parent.parent
W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_Detect.exe'
out=ROOT/'SD200W_SAIV_OSU107_Detect_Green.exe'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='506e1b5097bedf27c1c2a03a7f0fa111f14dd41aacb759f41a9968369734cbbe'
p=pefile.PE(data=original);b=bytearray(original)
subprocess.run(['as','--32','-o',str(W/'detect_green.o'),str(W/'detect_green.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'detect_green.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'detect_green.o'),str(W/'detect_green.bin')],check=True)
payload=(W/'detect_green.bin').read_bytes()
symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'detect_green.o')],text=True).splitlines() if len(t:=line.split())==3}
rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x240000
for va,expected,label in [(0x511584,'e8c7fcf4ff','refresh'),(0x51166c,'e8df19feff','reset')]:
 off=p.get_offset_from_rva(va-0x400000)
 assert b[off:off+5]==bytes.fromhex(expected)
 b[off:off+5]=b'\xe8'+struct.pack('<i',0x400000+rva+symbols[label]-va-5)
def align(n,a):return (n+a-1)//a*a
header=p.sections[-1].get_file_offset()+40
assert header+40<=p.OPTIONAL_HEADER.SizeOfHeaders and b[header:header+40]==bytes(40)
raw=align(len(b),p.OPTIONAL_HEADER.FileAlignment);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<8sIIIIIIHHI',b,header,b'.green',len(payload),rva,size,raw,0,0,0,0,0x60000020)
struct.pack_into('<H',b,p.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(p.sections)+1)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
report=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols)
(W/'detect_green_manifest.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
