"""Set the About version label, preserving all previous patches."""
from pathlib import Path
import hashlib
import json
import struct
import pefile

root = Path(__file__).resolve().parent.parent
source = root/'SD200W_SAIV.exe'
output = root/'SD200W_SAIV_OSU107.exe'
original = source.read_bytes()
assert hashlib.sha256(original).hexdigest() == '41ad45d3066238a7481e9f06ec09d6d8b8b0bc15f210729f9a5575b0ef2b2258'
pe = pefile.PE(data=original)
entries = [lang.data.struct for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries if kind.id==10
           for name in kind.directory.entries if str(name.name)=='TABOUTBOXNAV'
           for lang in name.directory.entries]
assert len(entries)==1
entry = entries[0]
blob = pe.get_data(entry.OffsetToData,entry.Size)
old_text = b'Version and build date: not available\x00'
new_text = b'Version: 1.0 OSU107 Sept.2026'
# The original Delphi caption includes two trailing NUL characters.
start = blob.index(b'\x0cLabelVersion')
caption = blob.index(b'\x07Caption\x06',start)
length_at = caption+9
length = blob[length_at]
old = blob[caption:length_at+1+length]
assert old[10:].rstrip(b'\x00') == b'Version and build date: not available'
new = b'\x07Caption\x06'+bytes([len(new_text)])+new_text
modified = blob[:caption]+new+blob[caption+len(old):]
assert modified[:caption]+old+modified[caption+len(new):] == blob
result = bytearray(original)
offset = pe.get_offset_from_rva(entry.OffsetToData)
result[offset:offset+entry.Size] = modified+bytes(len(blob)-len(modified))
size_offset = entry.get_field_absolute_offset('Size')
struct.pack_into('<I',result,size_offset,len(modified))
# Startup normally overwrites this label with FileVersion + build date.
# Skip only that caption setter, leaving all version-reading logic intact.
setter_rva = 0x1a47c9
setter = pe.get_offset_from_rva(setter_rva)
assert result[setter:setter+5] == bytes.fromhex('e88e31e9ff')
assert not any(e.type and setter_rva <= e.rva < setter_rva+5
               for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries)
result[setter:setter+5] = b'\x90'*5
checksum = pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
struct.pack_into('<I',result,checksum,pefile.PE(data=bytes(result)).generate_checksum())
output.write_bytes(result)
check = pefile.PE(str(output))
assert check.OPTIONAL_HEADER.CheckSum == check.generate_checksum()
assert new in check.get_data(entry.OffsetToData,len(modified))
allowed = set(range(offset,offset+len(blob))) | set(range(size_offset,size_offset+4)) | set(range(checksum,checksum+4)) | set(range(setter,setter+5))
assert len(original)==len(result)
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,result)))
assert source.read_bytes()==original
report = dict(output=output.name,version=new_text.decode(),sha256=hashlib.sha256(result).hexdigest(),
              validation='Only About version caption, its startup setter, resource size and checksum changed; all earlier patches preserved.')
(root/'analysis'/'osu107_version_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
