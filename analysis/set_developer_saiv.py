"""Change only the About dialog's Developer caption in the latest modified EXE."""
from pathlib import Path
import hashlib
import json
import struct
import pefile

root = Path(__file__).resolve().parent.parent
source = root / 'SD200W_diskguard_no_call_receive.exe'
output = root / 'SD200W_SAIV.exe'
original = source.read_bytes()
assert hashlib.sha256(original).hexdigest() == 'f3c7f926d76bda29a606771d4200cbde8411431faeb21010d8ac1e4d9fcc6648'
pe = pefile.PE(data=original)
old = b'\x07Caption\x06\x1eMorten Hammersland Programvare'
new = b'\x07Caption\x06\x07SAIV AS'
matches = []
for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    if kind.id != 10:
        continue
    for name in kind.directory.entries:
        for language in name.directory.entries:
            entry = language.data.struct
            blob = pe.get_data(entry.OffsetToData, entry.Size)
            if old in blob:
                matches.append((str(name.name), entry, blob))
assert len(matches) == 1
name, entry, blob = matches[0]
assert blob.startswith(b'TPF0') and b'\x07Caption\x06\nDeveloper:' in blob
assert blob.count(old) == 1
modified = blob.replace(old, new)
assert modified.replace(new, old) == blob
result = bytearray(original)
offset = pe.get_offset_from_rva(entry.OffsetToData)
result[offset:offset+entry.Size] = modified + bytes(len(blob)-len(modified))
size_offset = entry.get_field_absolute_offset('Size')
struct.pack_into('<I', result, size_offset, len(modified))
checksum_offset = pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
struct.pack_into('<I', result, checksum_offset, pefile.PE(data=bytes(result)).generate_checksum())
output.write_bytes(result)
check = pefile.PE(str(output))
assert check.OPTIONAL_HEADER.CheckSum == check.generate_checksum()
assert check.get_data(entry.OffsetToData, len(modified)) == modified
# Apart from this resource, its size and the checksum, every byte is preserved.
allowed = set(range(offset, offset+len(blob))) | set(range(size_offset,size_offset+4)) | set(range(checksum_offset,checksum_offset+4))
assert len(result) == len(original)
assert all(a == b or i in allowed for i,(a,b) in enumerate(zip(original,result)))
assert source.read_bytes() == original
report = dict(source=source.name,output=output.name,resource=name,
              developer='SAIV AS',sha256=hashlib.sha256(result).hexdigest(),
              validation='Only About caption resource, resource size, and PE checksum changed. Earlier patches remain byte-identical.')
(root/'analysis'/'saiv_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
