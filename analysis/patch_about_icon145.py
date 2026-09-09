"""Use the existing instrument ICO in About; preserve other DFM properties."""
from pathlib import Path
import ast,struct,hashlib,json,pefile
from PIL import Image
R=Path(__file__).resolve().parent.parent

def patch_about_icon(original):
 tree=ast.parse((R/'analysis/remove_phone_buttons.py').read_text())
 scope={'struct':struct}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='DfmReader'],type_ignores=[]),'dfm','exec'),scope)
 Reader=scope['DfmReader'];p=pefile.PE(data=bytes(original))
 entry=next(l.data.struct for k in p.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if str(n.name)=='TABOUTBOXNAV' for l in n.directory.entries)
 dfm=p.get_data(entry.OffsetToData,entry.Size);nodes=Reader(dfm).parse()
 cls,props,end=nodes['ProgramIcon'];assert cls=='TImage'
 ico=(R/'icon/ctd_in_Cage.ico').read_bytes()
 assert struct.unpack_from('<HH',ico)==(0,1)
 # The ICO contains PNG frames. This Delphi TIcon reader needs a classic DIB.
 # Re-encode the same RGBA pixels, with the legacy transparency mask as well.
 art=Image.open(R/'icon/ctd_in_Cage.ico').ico.getimage((64,64)).convert('RGBA')
 rgba=art.tobytes();xor=art.tobytes('raw','BGRA',0,-1)
 mask=bytearray(64*8)
 for y in range(64):
  for x in range(64):
   if rgba[(y*64+x)*4+3]==0:mask[(63-y)*8+x//8]|=0x80>>(x%8)
 pixels=struct.pack('<IiiHHIIiiII',40,64,128,1,32,0,len(xor),0,0,0,0)+xor+mask
 single=struct.pack('<HHHBBBBHHII',0,1,1,64,64,0,0,1,32,len(pixels),22)+pixels
 import io
 assert Image.open(io.BytesIO(single)).convert('RGBA').tobytes()==rgba
 picture=b'\x05TIcon'+single
 # This Delphi version centres TIcon using the system 32px size even for 64px
 # artwork. Draw at the existing top-left so the full 64px icon stays inside.
 changes={'Picture.Data':b'\x0a'+struct.pack('<I',len(picture))+picture,'Stretch':b'\x08','Center':b'\x08'}
 edits=[];found=set()
 for key,a,v,z in props:
  if key in changes:edits.append((v,z,changes[key]));found.add(key)
 extra=b''
 for key in changes.keys()-found:
  encoded=key.encode();extra+=bytes([len(encoded)])+encoded+changes[key]
 if extra:edits.append((end,end,extra))
 updated=dfm
 for a,z,value in sorted(edits,reverse=True):updated=updated[:a]+value+updated[z:]
 after=Reader(updated).parse();assert nodes.keys()==after.keys()
 for name,(_,pr,_) in nodes.items():
  expected={key:dfm[v:z] for key,a,v,z in pr}
  if name=='ProgramIcon':expected.update(changes)
  assert expected=={key:updated[v:z] for key,a,v,z in after[name][1]},name
 b=bytearray(original);allowed=set()
 def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
 def align(n,a):return (n+a-1)//a*a
 last=p.sections[-1];rva=p.OPTIONAL_HEADER.SizeOfImage
 raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
 padded=align(len(updated),p.OPTIONAL_HEADER.FileAlignment)
 put(entry.get_file_offset(),struct.pack('<II',rva,len(updated)))
 put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(updated)))
 put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+padded))
 put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(updated),p.OPTIONAL_HEADER.SectionAlignment)))
 res=p.OPTIONAL_HEADER.DATA_DIRECTORY[2]
 put(res.get_field_absolute_offset('Size'),struct.pack('<I',rva+len(updated)-res.VirtualAddress))
 b.extend(bytes(raw-len(b))+updated+bytes(padded-len(updated)))
 assert all(x==b[i] or i in allowed for i,x in enumerate(original))
 report={'icon':'icon/ctd_in_Cage.ico','icon_sha256':hashlib.sha256(ico).hexdigest(),'size':[64,64],
         'original_icon_pixels_preserved':True,'legacy_DIB_encoding':True,'other_about_properties_preserved':True,
         'existing_runtime_bytes_preserved_except_resource_directory_and_PE_sizes':True}
 (R/'analysis/about_icon145_patch_validation.json').write_text(json.dumps(report,indent=2))
 return b
