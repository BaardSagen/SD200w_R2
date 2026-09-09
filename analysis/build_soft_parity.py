from pathlib import Path
import pefile,hashlib,struct,subprocess,json
R=Path(__file__).resolve().parent.parent;W=R/'analysis'
source=R/'SD200W_SAIV_v1.0.4_MenuDetect_Sept2026.exe';out=R/'SD200W_SAIV_v1.0.5_SoftParity_Sept2026.exe'
original=source.read_bytes();expected='eb7b28cf8d82acab316bc2f74638c637f311f9cb3af2dbd9a39b59181028ee64';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x298000
subprocess.run(['as','--32','-o',str(W/'soft_parity.o'),str(W/'soft_parity.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'soft_parity.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'soft_parity.o'),str(W/'soft_parity.bin')],check=True)
payload=(W/'soft_parity.bin').read_bytes();symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'soft_parity.o')],text=True).splitlines() if len(t:=line.split())==3};allowed=set();patches=[]
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def hook(va,old,label):
 off=p.get_offset_from_rva(va-0x400000);assert b[off]==0xe8 and va+5+struct.unpack_from('<i',b,off+1)[0]==old
 put(off,b'\xe8'+struct.pack('<i',0x400000+rva+symbols[label]-va-5));patches.append((va-0x400000,5))
for va in (0x47e6b2,0x47e87a,0x47e8ee,0x47f427):hook(va,0x693000,'configure')
hook(0x47fc73,0x407b4c,'receive');hook(0x4800ce,0x4043e8,'send_string')
for block in p.DIRECTORY_ENTRY_BASERELOC:
 for e in block.entries:assert not (e.type and any(a<=e.rva<a+n for a,n in patches))
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if (k.id==10 and str(n.name)=='TABOUTBOXNAV') or k.id==16:
    e=l.data.struct;data=bytearray(p.get_data(e.OffsetToData,e.Size));encoding='utf-16le' if k.id==16 else 'ascii';old='1.0.4 Sept.2026'.encode(encoding);assert old in data;data=data.replace(old,'1.0.5 Sept.2026'.encode(encoding))
    if k.id==16:start=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,start+8,0x10000,0x50000,0x10000,0x50000)
    put(p.get_offset_from_rva(e.OffsetToData),data)
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)));put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size));put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)));put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original));out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum();assert source.read_bytes()==original
m=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols,scope='Logical 7E1 through physical 8N1; ordinary 8N1 bytes untouched; menu probe retained',validation='Pending')
(W/'soft_parity_manifest.json').write_text(json.dumps(m,indent=2));print(out.name,m['sha256'])
