from pathlib import Path
import pefile,hashlib,struct,subprocess,json
R=Path(__file__).resolve().parent.parent;W=R/'analysis'
source=R/'SAIV_Instrument_Terminal_v1.3.1_Sept2026.exe';out=R/'SAIV_Instrument_Terminal_v1.3.2_Sept2026.exe'
original=source.read_bytes();expected='5b6c0de8102d6bd696ae3a396231f9a225c28bbff69cd5441dcda4d253ee4af5';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;hook=0x1140c9;old=p.get_data(hook,9);assert old[0]==0xe8 and old[5:]==b'\x90'*4
previous=hook+5+struct.unpack('<i',old[1:5])[0]
subprocess.run(['as','--32','--defsym',f'PAYLOAD_RVA={rva}','--defsym',f'PREVIOUS_RVA={previous}','-o',str(W/'last_com_port.o'),str(W/'last_com_port.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'last_com_port.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'last_com_port.o'),str(W/'last_com_port.bin')],check=True)
payload=(W/'last_com_port.bin').read_bytes();allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
put(p.get_offset_from_rva(hook),b'\xe8'+struct.pack('<i',rva-hook-5))
for block in p.DIRECTORY_ENTRY_BASERELOC:
 for e in block.entries:assert not(e.type and hook<=e.rva<hook+9)
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;data=bytearray(p.get_data(e.OffsetToData,e.Size));encoding='utf-16le' if k.id==16 else 'ascii';oldver='1.3.1 Sept.2026'.encode(encoding);assert oldver in data;data=data.replace(oldver,'1.3.2 Sept.2026'.encode(encoding))
    if k.id==16:
     at=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,at+8,0x10003,0x20000,0x10003,0x20000)
    put(p.get_offset_from_rva(e.OffsetToData),data)
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(v==b[i] or i in allowed for i,v in enumerate(original));out.write_bytes(b);q=pefile.PE(str(out));assert q.verify_checksum();assert q.get_data(0x10a000,0x3000)==p.get_data(0x10a000,0x3000)
m=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,hook_rva=hook,previous_rva=previous,dll='SIT_Import131.dll',dll_sha256=hashlib.sha256((R/'SIT_Import131.dll').read_bytes()).hexdigest(),ctd_formula_bytes_unchanged=True)
(W/'last_com_port_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
