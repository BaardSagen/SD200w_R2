from pathlib import Path
import pefile,subprocess,hashlib,struct,json,ast,io
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe';out=ROOT/'SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe'
original=source.read_bytes();expected='53841d3d6e515d9a659a93c49b00bacff651a83092c1d4453a866a755778f4e6';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x29f000
payload=b''
allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def patch(va,old,new):off=p.get_offset_from_rva(va-0x400000);assert b[off:off+len(old)]==old,(hex(va),b[off:off+len(old)].hex());put(off,new)
entries=[(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
for kind,name,e in entries:
 if (kind==10 and name=='TABOUTBOXNAV') or kind==16:
  data=bytearray(p.get_data(e.OffsetToData,e.Size));old=('1.1.1 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');new=('1.1.2 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');assert old in data;data=data.replace(old,new)
  if kind==16:
   start=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,start+8,0x10001,0x20000,0x10001,0x20000)
  put(p.get_offset_from_rva(e.OffsetToData),data)
icon_path=ROOT/'icon/ctd_in_Cage.ico';ico=icon_path.read_bytes()
assert struct.unpack_from('<HH',ico)==(0,1)
count=struct.unpack_from('<H',ico,4)[0];assert count==9
payload=bytearray()
def add(data):
 payload.extend(bytes((-len(payload))%4));addr=rva+len(payload);payload.extend(data);return addr
resbase=p.OPTIONAL_HEADER.DATA_DIRECTORY[2].VirtualAddress
icons=[]
for index in range(count):
 record=ico[6+16*index:22+16*index];size,off=struct.unpack_from('<II',record,8)
 image=ico[off:off+size];assert len(image)==size
 image_rva=add(image);data_rva=add(struct.pack('<IIII',image_rva,size,0,0))
 lang_rva=add(struct.pack('<IIHHHHII',0,0,0,0,0,1,1044,data_rva-resbase))
 icons.append((index+1,record,lang_rva))
icon_dir=struct.pack('<IIHHHH',0,0,0,0,0,count)+b''.join(struct.pack('<II',idx,0x80000000|(lang-resbase)) for idx,record,lang in icons)
icon_dir_rva=add(icon_dir)
root_icon=next(e for e in p.DIRECTORY_ENTRY_RESOURCE.entries if e.id==3)
put(root_icon.struct.get_file_offset()+4,struct.pack('<I',0x80000000|(icon_dir_rva-resbase)))
group=struct.pack('<HHH',0,1,count)+b''.join(record[:12]+struct.pack('<H',idx) for idx,record,lang in icons)
group_rva=add(group);group_res=next(e for kind,name,e in entries if kind==14 and name=='MAINICON')
put(group_res.get_file_offset(),struct.pack('<II',group_rva,len(group)))
# Delphi TSpeedButton: normal + disabled bitmap frames, existing two-glyph setting.
t=ast.parse((W/'remove_phone_buttons.py').read_text());exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
res=next(e for kind,name,e in entries if kind==10 and name=='TFORM1');blob=p.get_data(res.OffsetToData,res.Size);nodes=DfmReader(blob).parse()
art=Image.open(icon_path).ico.getimage((20,20)).convert('RGBA');alpha=art.getchannel('A')
normal=Image.new('RGB',(20,20),(240,240,240));normal.paste(art,mask=alpha)
disabled=Image.blend(ImageOps.grayscale(normal).convert('RGB'),Image.new('RGB',(20,20),(240,240,240)),.45)
transparent=alpha.point(lambda a:255 if a==0 else 0)
for frame in (normal,disabled):frame.paste((255,0,255),(0,0,20,20),transparent)
sheet=Image.new('RGB',(40,20));sheet.paste(normal,(0,0));sheet.paste(disabled,(20,0));stream=io.BytesIO();sheet.save(stream,format='BMP');bmp=stream.getvalue()
_,props,_=nodes['sbtnInstrument'];key,st,v,end=next(t for t in props if t[0]=='Glyph.Data')
value=b'\x0a'+struct.pack('<II',len(bmp)+4,len(bmp))+bmp
modified=blob[:v]+value+blob[end:];after=DfmReader(modified).parse();assert set(after)==set(nodes)
form_rva=add(modified);put(res.get_file_offset(),struct.pack('<II',form_rva,len(modified)))
put(p.OPTIONAL_HEADER.DATA_DIRECTORY[2].get_field_absolute_offset('Size'),struct.pack('<I',rva+len(payload)-resbase))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original))
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum();assert source.read_bytes()==original
check=pefile.PE(str(out));assert len(next(e for e in check.DIRECTORY_ENTRY_RESOURCE.entries if e.id==3).directory.entries)==count
manifest=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),icon='icon/ctd_in_Cage.ico',icon_sha256=hashlib.sha256(ico).hexdigest(),icon_sizes=sorted(Image.open(icon_path).ico.sizes()),button='sbtnInstrument',glyph_size=[20,20],validation='Resource-only patch; original code preserved byte for byte')
(W/'instrument_icon_manifest.json').write_text(json.dumps(manifest,indent=2));print(out.name,manifest['sha256'])
