"""Start the latest modified executable on the Instrument/terminal page."""
from pathlib import Path
import hashlib
import json
import struct
import pefile

root = Path(__file__).resolve().parent.parent
source = root/'SD200W_SAIV_OSU107_final.exe'
output = root/'SD200W_SAIV_OSU107_Instrument.exe'
original = source.read_bytes()
assert hashlib.sha256(original).hexdigest() == '065bb0c40f99021b55312947e9e684b92bbecc8b7d340e30aeebcc39b4f2854e'
pe = pefile.PE(data=original)
# FormCreate sets Notebook1.PageIndex to 3, overriding the DFM's page 2.
# The Instrument toolbar handler at 0x5a0ff0 selects page 2 on the same Notebook.
startup = pe.get_offset_from_rva(0x195d43)
assert original[startup:startup+19] == bytes.fromhex('8b45fc8b800c030000ba03000000e89ac1ecff')
toolbar = pe.get_offset_from_rva(0x1a0ff3)
assert original[toolbar:toolbar+16] == bytes.fromhex('ba020000008b830c030000e8ed0eecff')
result = bytearray(original)
changed = pe.get_offset_from_rva(0x195d4d)
result[changed] = 2
assert struct.unpack_from('<I',result,changed)[0] == struct.unpack_from('<I',original,toolbar+1)[0] == 2
checksum = pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
struct.pack_into('<I',result,checksum,pefile.PE(data=bytes(result)).generate_checksum())
output.write_bytes(result)
check = pefile.PE(str(output))
assert check.OPTIONAL_HEADER.CheckSum == check.generate_checksum()
allowed = {changed} | set(range(checksum,checksum+4))
assert len(result)==len(original)
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,result)))
assert source.read_bytes()==original
report = dict(source=source.name,output=output.name,sha256=hashlib.sha256(result).hexdigest(),
              startup_page=2,validation='Startup selects the same Notebook and page as the Instrument toolbar button. Only one code byte and the PE checksum changed. All earlier modifications preserved.')
(root/'analysis'/'instrument_start_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
