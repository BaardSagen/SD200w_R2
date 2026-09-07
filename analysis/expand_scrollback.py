"""Increase both terminal history limits by 20x, preserving previous patches."""
from pathlib import Path
import hashlib, json, struct
import pefile

root=Path(__file__).resolve().parent.parent
source=root/'SD200W_SAIV_OSU107_Instrument_v2.exe'
output=root/'SD200W_SAIV_OSU107_History.exe'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='d695978e87cdd6224f9a856b8ec42e770d8513d2226841b4a07d04a2a2475659'
p=pefile.PE(data=original)
section=p.sections[-1]
assert section.Name.rstrip(b'\x00')==b'.startui'
rel=(section.Misc_VirtualSize+15)//16*16
rva=section.VirtualAddress+rel
# Count > 2000: remove oldest line and recheck; otherwise append as before.
payload=b'\x3d'+struct.pack('<I',2000)
payload+=b'\x0f\x8f'+struct.pack('<i',0x19bcb8-(rva+11))
payload+=b'\xe9'+struct.pack('<i',0x19bccd-(rva+16))
off=section.PointerToRawData+rel
assert rel+len(payload)<=section.SizeOfRawData
assert original[off:off+len(payload)]==bytes(len(payload))
hook_rva=0x19bcc8
hook=p.get_offset_from_rva(hook_rva)
assert original[hook:hook+5]==bytes.fromhex('83f8647feb')
alternate=p.get_offset_from_rva(0x19bc21)
assert original[alternate-1:alternate+4]==bytes.fromhex('bf84030000')
b=bytearray(original)
b[off:off+len(payload)]=payload
b[hook:hook+5]=b'\xe9'+struct.pack('<i',rva-hook_rva-5)
struct.pack_into('<I',b,alternate,18000)
virtualsize=section.get_field_absolute_offset('Misc_VirtualSize')
struct.pack_into('<I',b,virtualsize,rel+len(payload))
checksum=p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
struct.pack_into('<I',b,checksum,pefile.PE(data=bytes(b)).generate_checksum())
output.write_bytes(b)
assert pefile.PE(str(output)).verify_checksum()
allowed=set(range(off,off+len(payload)))|set(range(hook,hook+5))|set(range(alternate,alternate+4))|set(range(virtualsize,virtualsize+4))|set(range(checksum,checksum+4))
assert len(original)==len(b)
assert all(x==y or i in allowed for i,(x,y) in enumerate(zip(original,b)))
assert source.read_bytes()==original
report=dict(source=source.name,output=output.name,sha256=hashlib.sha256(b).hexdigest(),
            terminal_limit=dict(old=100,new=2000),alternate_memo_limit=dict(old=900,new=18000),
            trampoline_rva=rva,notes='Limits apply before appending the current line. Resources, prior guard and startup instructions remain unchanged.')
(root/'analysis'/'scrollback_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
