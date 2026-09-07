from pathlib import Path
import pefile,struct,hashlib,json
root=Path(__file__).resolve().parent.parent
source=root/'SD200W_SAIV_OSU107_NoHandshake.exe';out=root/'SD200W_SAIV_v1.0.1_Sept2026.exe'
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()=='3908bded6ca05244bee62e4eded3a3042b8cff9bf043c003012b44fd63aa8599'
p=pefile.PE(data=original);b=bytearray(original);version='1.0.1 Sept.2026'
allowed=set()
def write(off,data):
 b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def align(n,a=4):return (n+a-1)//a*a
entries=[(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
about=[e for k,n,e in entries if k==10 and n=='TABOUTBOXNAV'];assert len(about)==1
entry=about[0];blob=p.get_data(entry.OffsetToData,entry.Size)
old=b'Version: 1.0 OSU107 Sept.2026';new=('Version: '+version).encode();needle=b'\x07Caption\x06'+bytes([len(old)])+old
assert blob.count(needle)==1
updated=blob.replace(needle,b'\x07Caption\x06'+bytes([len(new)])+new)
write(p.get_offset_from_rva(entry.OffsetToData),updated+bytes(len(blob)-len(updated)))
write(entry.get_field_absolute_offset('Size'),struct.pack('<I',len(updated)))
assert p.get_data(0x1a47c9,5)==b'\x90'*5
# Rebuild the VERSIONINFO tree with correct Unicode lengths and DWORD alignment.
e=[e for k,n,e in entries if k==16];assert len(e)==1;e=e[0];raw=p.get_data(e.OffsetToData,e.Size)
def parse(pos):
 length,vlen,typ=struct.unpack_from('<HHH',raw,pos);end=pos+length
 q=pos+6;z=q
 while raw[z:z+2]!=b'\x00\x00':z+=2
 key=raw[q:z].decode('utf-16le');q=align(z+2);size=vlen*(2 if typ else 1)
 value=raw[q:q+size];q=align(q+size);kids=[]
 while q+6<=end and struct.unpack_from('<H',raw,q)[0]:
  node,nextpos=parse(q);kids.append(node);q=align(nextpos)
 return [key,typ,value,kids],end
node,_=parse(0)
def update(n):
 key,typ,value,kids=n
 if key in ('FileVersion','ProductVersion'):n[2]=(version+'\x00').encode('utf-16le')
 if key=='VS_VERSION_INFO':
  value=bytearray(value);assert struct.unpack_from('<I',value)[0]==0xfeef04bd
  struct.pack_into('<IIII',value,8,0x00010000,0x00010000,0x00010000,0x00010000);n[2]=bytes(value)
 for child in kids:update(child)
update(node)
def encode(n):
 key,typ,value,kids=n;x=bytearray(b'\x00'*6+(key+'\x00').encode('utf-16le'));x.extend(bytes(align(len(x))-len(x)));x.extend(value)
 for child in kids:x.extend(bytes(align(len(x))-len(x)));x.extend(encode(child))
 struct.pack_into('<HHH',x,0,len(x),len(value)//2 if typ else len(value),typ);return bytes(x)
payload=encode(node);last=p.sections[-1];rva=p.OPTIONAL_HEADER.SizeOfImage;off=last.PointerToRawData+rva-last.VirtualAddress
assert off>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
write(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
write(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
write(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
write(e.get_field_absolute_offset('OffsetToData'),struct.pack('<I',rva));write(e.get_field_absolute_offset('Size'),struct.pack('<I',len(payload)))
b.extend(bytes(off-len(b))+payload+bytes(size-len(payload)))
write(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original))
# No instruction bytes changed, including all earlier communication patches.
for sec in p.sections:
 if sec.Name.rstrip(b'\x00')==b'CODE':assert b[sec.PointerToRawData:sec.PointerToRawData+sec.SizeOfRawData]==original[sec.PointerToRawData:sec.PointerToRawData+sec.SizeOfRawData]
out.write_bytes(b);check=pefile.PE(str(out));assert check.verify_checksum()
assert check.VS_FIXEDFILEINFO[0].FileVersionMS==0x10000 and check.VS_FIXEDFILEINFO[0].FileVersionLS==0x10000
print(out.name)
for group in check.FileInfo:
 for info in group:
  if hasattr(info,'StringTable'):
   for table in info.StringTable:print(table.entries)
(root/'analysis/version_1_0_1_manifest.json').write_text(json.dumps(dict(output=out.name,version=version,numeric_version='1.0.1.0',sha256=hashlib.sha256(b).hexdigest()),indent=2))
