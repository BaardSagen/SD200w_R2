from pathlib import Path
import hashlib, json, struct, subprocess
import pefile

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_final.exe'
output=ROOT/'SD200W_SAIV_OSU107_Instrument_v2.exe'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='065bb0c40f99021b55312947e9e684b92bbecc8b7d340e30aeebcc39b4f2854e'
p=pefile.PE(data=original)
def align(n,a): return (n+a-1)//a*a
rva=p.OPTIONAL_HEADER.SizeOfImage
assert rva==0x23e000
assert p.get_data(0x195d4c,5)==bytes.fromhex('ba03000000'), 'Must preserve original startup page'
subprocess.run(['as','--32','-o',str(WORK/'deferred_start.o'),str(WORK/'start_instrument_deferred.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(WORK/'deferred_start.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(WORK/'deferred_start.o'),str(WORK/'deferred_start.bin')],check=True)
payload=(WORK/'deferred_start.bin').read_bytes()
symbols={}
for line in subprocess.check_output(['nm','-n',str(WORK/'deferred_start.o')],text=True).splitlines():
    items=line.split()
    if len(items)==3: symbols[items[2]]=int(items[0],16)
b=bytearray(original)
hook_rva=0x1a4c51
off=p.get_offset_from_rva(hook_rva)
assert b[off:off+5]==bytes.fromhex('5f5e5b8be5')
assert not any(e.type and hook_rva<=e.rva<hook_rva+5 for block in p.DIRECTORY_ENTRY_BASERELOC for e in block.entries)
b[off:off+5]=b'\xe9'+struct.pack('<i',rva-hook_rva-5)
hdr=p.sections[-1].get_file_offset()+40
assert hdr+40<=p.OPTIONAL_HEADER.SizeOfHeaders and b[hdr:hdr+40]==bytes(40)
raw=align(len(b),p.OPTIONAL_HEADER.FileAlignment)
size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<8sIIIIIIHHI',b,hdr,b'.startui',len(payload),rva,size,raw,0,0,0,0,0xe0000060)
struct.pack_into('<H',b,p.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(p.sections)+1)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
output.write_bytes(b)
q=pefile.PE(str(output))
assert q.OPTIONAL_HEADER.CheckSum==q.generate_checksum()
for sec in p.sections:
    for i in range(sec.PointerToRawData,sec.PointerToRawData+sec.SizeOfRawData):
        assert original[i]==b[i] or off<=i<off+5
assert source.read_bytes()==original
manifest=dict(output=output.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols,
              validation='Original startup restored; one-time timer invokes original Instrument handler after FormActivate returns. All previous changes preserved.')
(WORK/'deferred_start_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
