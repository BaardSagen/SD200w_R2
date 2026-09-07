"""Prioritize None then Even in the existing concurrent per-port search."""
from pathlib import Path
import hashlib,json,struct,pefile
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'SD200W_SAIV_OSU107_Detect_Green.exe'
output=ROOT/'SD200W_SAIV_OSU107_Detect_Priority.exe'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='97186b304ad9c3c0548fc034435361ff276b42c1fd300a46ddd44df05c993d7a'
p=pefile.PE(data=original);b=bytearray(original)
offset=p.get_offset_from_rva(0x1b1374)
assert b[offset:offset+2]==b'en'
b[offset:offset+2]=b'ne'
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
output.write_bytes(b)
assert pefile.PE(str(output)).verify_checksum()
rates=struct.unpack('<8I',p.get_data(0x1b13b4,32))
report=dict(output=output.name,sha256=hashlib.sha256(b).hexdigest(),sequence=[dict(baud=r,parity=parity) for r in rates for parity in ['None','Even']],
 concurrency='Existing per-port worker construction at 0x5116d6 and Resume at 0x51172e retained; no waits between launching workers.',
 changes=[dict(rva='0x1b1374',before='en',after='ne')])
(ROOT/'analysis'/'detect_priority_manifest.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
