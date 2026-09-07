"""Replace the company name in the Disclaimer's static Delphi string."""
from pathlib import Path
import hashlib
import json
import struct
import pefile

root = Path(__file__).resolve().parent.parent
source = root/'SD200W_SAIV_OSU107.exe'
output = root/'SD200W_SAIV_OSU107_final.exe'
original = source.read_bytes()
assert hashlib.sha256(original).hexdigest() == 'f441885eaa7ed3eecb2c6a7d73972a912b20bb7927c5531496325c38dfca45e9'
pe = pefile.PE(data=original)
offset = pe.get_offset_from_rva(0x109e68)
assert original[offset:offset+11] == b'Disclaimer:'
assert original[offset-8:offset-4] == b'\xff'*4
length = struct.unpack_from('<I',original,offset-4)[0]
assert length == 217
old = original[offset:offset+length]
assert old.count(b'Morten Hammersland Programvare') == 1
new = old.replace(b'Morten Hammersland Programvare',b'SAIV A/S')
result = bytearray(original)
struct.pack_into('<I',result,offset-4,len(new))
result[offset:offset+length+1] = new+bytes(length+1-len(new))
checksum = pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
struct.pack_into('<I',result,checksum,pefile.PE(data=bytes(result)).generate_checksum())
output.write_bytes(result)
check = pefile.PE(str(output))
assert check.OPTIONAL_HEADER.CheckSum == check.generate_checksum()
assert result[offset+len(new)] == 0
assert struct.unpack_from('<I',result,offset-4)[0] == len(new)
allowed = set(range(offset-4,offset+length+1)) | set(range(checksum,checksum+4))
assert len(original) == len(result)
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,result)))
assert source.read_bytes() == original
report = dict(source=source.name,output=output.name,disclaimer=new.decode('ascii'),
              sha256=hashlib.sha256(result).hexdigest(),
              validation='Only Disclaimer string, its length, and PE checksum changed; previous changes preserved.')
(root/'analysis'/'disclaimer_saiv_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
