"""Translate refresh reply messages without changing executable code or layout."""
from pathlib import Path
import hashlib,json,struct,pefile
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'SD200W_SAIV_OSU107_RefreshReply.exe'
out=ROOT/'SD200W_SAIV_OSU107_RefreshReply_EN.exe'
b=bytearray(source.read_bytes())
assert hashlib.sha256(b).hexdigest()=='ba1f6d5ce50a14155199da2d9a48d15bcf0f165bedcc158966889eb3c47cd551'
p=pefile.PE(data=bytes(b));m=json.loads((ROOT/'analysis/refresh_reply_manifest.json').read_text())
messages={
 'logging_message':'Stop logging and wait for the current sample to finish before refreshing the disk. Then click Download again.',
 'timeout_message':'Disk refresh was not confirmed. Check the terminal response.'
}
changes=[]
for name,text in messages.items():
 offset=p.get_offset_from_rva(m['section_rva']+m['symbols'][name])
 end=b.index(0,offset);new=text.encode('ascii');assert len(new)<=end-offset
 b[offset:end]=new+bytes(end-offset-len(new))
 assert bytes(b[offset:b.index(0,offset)]).decode('ascii')==text
 changes.append({'symbol':name,'message':text,'offset':offset,'size':end-offset})
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
allowed=set(range(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')+4))
for c in changes:allowed.update(range(c['offset'],c['offset']+c['size']))
assert all(a==z or i in allowed for i,(a,z) in enumerate(zip(source.read_bytes(),b)))
report={'output':out.name,'sha256':hashlib.sha256(b).hexdigest(),'messages':changes,'verification':'Only message bytes and PE checksum changed; offsets and code preserved.'}
(ROOT/'analysis/refresh_reply_en_manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
