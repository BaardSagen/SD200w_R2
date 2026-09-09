from pathlib import Path
import pefile,subprocess,hashlib,struct,json,ast
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe';out=ROOT/'SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe'
original=source.read_bytes();expected='e85cdb6119350e249a17b1eda037640a04ee2c12be210f2cc91a474bbd3cf6b7';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva>=0x29f000
payload=b''
allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def patch(va,old,new):off=p.get_offset_from_rva(va-0x400000);assert b[off:off+len(old)]==old,(hex(va),b[off:off+len(old)].hex());put(off,new)
entries=[(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
TITLE='SAIV Instrument Terminal'
payload=bytearray()
def add(data):
 payload.extend(bytes((-len(payload))%4));addr=rva+len(payload);payload.extend(data);return addr
# A static Delphi AnsiString can also serve the plain Windows message captions.
name_rva=add(struct.pack('<iI',-1,len(TITLE))+TITLE.encode()+b'\0')+8
relocs={e.rva for block in p.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3}
assert 0x1afb70 in relocs
patch(0x5afb70,struct.pack('<I',0x459f14),struct.pack('<I',0x400000+name_rva))
for at,oldrva in [(0x23d1c1,0x23d218),(0x29225b,0x2922ce),(0x292516,0x2922ce)]:
 assert at not in relocs
 patch(0x400000+at,struct.pack('<I',oldrva),struct.pack('<I',name_rva))
t=ast.parse((W/'remove_phone_buttons.py').read_text());exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
def rebuild_version(data,offset=0):
 length,vlen,typ=struct.unpack_from('<HHH',data,offset);end=offset+length;pos=offset+6;key_end=pos
 while data[key_end:key_end+2]!=b'\0\0':key_end+=2
 key=data[pos:key_end].decode('utf-16le');pos=(key_end+2+3)&~3
 size=vlen*(2 if typ==1 else 1);value=data[pos:pos+size];pos=(pos+size+3)&~3
 children=[]
 while pos+6<=end:
  childlen=struct.unpack_from('<H',data,pos)[0]
  if not childlen:break
  children.append(rebuild_version(data,pos));pos=(pos+childlen+3)&~3
 updates={'FileDescription':TITLE,'InternalName':TITLE,'ProductName':TITLE,'OriginalFilename':out.name,'FileVersion':'1.1.3 Sept.2026','ProductVersion':'1.1.3 Sept.2026'}
 if key in updates:value=(updates[key]+'\0').encode('utf-16le');vlen=len(value)//2
 if key=='VS_VERSION_INFO':
  value=bytearray(value);assert struct.unpack_from('<I',value)[0]==0xfeef04bd;struct.pack_into('<IIII',value,8,0x10001,0x30000,0x10001,0x30000)
 result=bytearray(struct.pack('<HHH',0,vlen,typ)+(key+'\0').encode('utf-16le'));result.extend(bytes((-len(result))%4));result.extend(value)
 for child in children:result.extend(bytes((-len(result))%4));result.extend(child)
 struct.pack_into('<H',result,0,len(result));return bytes(result)
for kind,name,e in entries:
 data=p.get_data(e.OffsetToData,e.Size);updated=None
 if kind==16:updated=rebuild_version(data)
 elif kind==10 and name in ('TFORM1','TABOUTBOXNAV'):
  nodes=DfmReader(data).parse();edits=[]
  for node,(cls,props,end) in nodes.items():
   for key,st,v,z in props:
    if key=='Caption' and node in ('Form1','ProductName'):edits.append((v,z,b'\x06'+bytes([len(TITLE)])+TITLE.encode()))
    elif key=='Caption' and b'1.1.2 Sept.2026' in data[v:z]:edits.append((v,z,data[v:z].replace(b'1.1.2 Sept.2026',b'1.1.3 Sept.2026')))
  updated=data
  for v,z,value in sorted(edits,reverse=True):updated=updated[:v]+value+updated[z:]
  assert set(DfmReader(updated).parse())==set(nodes)
 if updated is not None:
  addr=add(updated);put(e.get_file_offset(),struct.pack('<II',addr,len(updated)))
put(p.OPTIONAL_HEADER.DATA_DIRECTORY[2].get_field_absolute_offset('Size'),struct.pack('<I',rva+len(payload)-p.OPTIONAL_HEADER.DATA_DIRECTORY[2].VirtualAddress))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original))
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum();assert source.read_bytes()==original
check=pefile.PE(str(out))
strings=next(table.entries for fi in check.FileInfo for item in fi if hasattr(item,'StringTable') for table in item.StringTable)
assert strings[b'ProductName']==TITLE.encode() and strings[b'OriginalFilename']==out.name.encode()
manifest=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),title=TITLE,name_rva=name_rva,validation='Pending GUI check; resource and name pointer changes only')
(W/'saiv_name_manifest.json').write_text(json.dumps(manifest,indent=2));print(out.name,manifest['sha256'])
