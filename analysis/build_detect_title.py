from pathlib import Path
import pefile,subprocess,hashlib,struct,json
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_v1.1.0_SelectG_Sept2026.exe';out=ROOT/'SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe'
original=source.read_bytes();expected='4ee2d90fe1dc79dd9ef6f3f95ac2102769f4382712f8e8cfb57eea9db8d5f037';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x29e000
payload=b''
allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def patch(va,old,new):off=p.get_offset_from_rva(va-0x400000);assert b[off:off+len(old)]==old,(hex(va),b[off:off+len(old)].hex());put(off,new)
entries=[(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
for kind,name,e in entries:
 if (kind==10 and name=='TABOUTBOXNAV') or kind==16:
  data=bytearray(p.get_data(e.OffsetToData,e.Size));old=('1.1.0 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');new=('1.1.1 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');assert old in data;data=data.replace(old,new)
  if kind==16:
   start=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,start+8,0x10001,0x10000,0x10001,0x10000)
  put(p.get_offset_from_rva(e.OffsetToData),data)
title='Find communication speed - Double-click green ports to open'
res=next(e for kind,name,e in entries if kind==10 and name=='TDLGAUTOBAUD')
blob=p.get_data(res.OffsetToData,res.Size);old=b'\x06\x18Find communication speed';assert blob.count(old)==1
payload=blob.replace(old,b'\x06'+bytes([len(title)])+title.encode('ascii'))
put(res.get_file_offset(),struct.pack('<II',rva,len(payload)))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original))
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum();assert source.read_bytes()==original
manifest=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),title=title,resource_rva=rva,validation='Resource-only patch; all original bytes outside explicitly changed PE metadata and resources preserved')
(W/'detect_title_manifest.json').write_text(json.dumps(manifest,indent=2));print(out.name,manifest['sha256'])
