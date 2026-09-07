from pathlib import Path
import hashlib,json,struct,subprocess,pefile
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_Blue_ScrollLine.exe'
out=ROOT/'SD200W_SAIV_OSU107_LoggerDetect.exe'
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()=='4d78d5f0128ed733b030ad13b9236dcb7e92f8304f16e0f2869e11b3b70daacf'
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x283000
subprocess.run(['as','--32','-o',str(W/'logger_detect.o'),str(W/'logger_detect.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'logger_detect.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'logger_detect.o'),str(W/'logger_detect.bin')],check=True)
payload=(W/'logger_detect.bin').read_bytes()
symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'logger_detect.o')],text=True).splitlines() if len(t:=line.split())==3}
for va,expected,label,op in [(0x503a37,'e888c5f7ff','passive',0xe8),(0x50387d,'e8820cf0ff','recognize',0xe8),(0x5031b0,'538bda0fb64071','label',0xe9),(0x5039b2,'e84daff7ff','delayed_open',0xe8)]:
 off=p.get_offset_from_rva(va-0x400000);assert b[off:off+len(bytes.fromhex(expected))]==bytes.fromhex(expected)
 b[off:off+len(bytes.fromhex(expected))]=bytes([op])+struct.pack('<i',0x400000+rva+symbols[label]-va-5)+b'\x90'*(len(bytes.fromhex(expected))-5)
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
m=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols)
(W/'logger_detect_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
