"""Apply a restrained blue palette to Delphi form resources, preserving code."""
from pathlib import Path
import ast,hashlib,json,struct,pefile,sys
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_Detect_Rows.exe'
scroll_line='--scroll-line' in sys.argv
classic_text='--classic-text' in sys.argv or scroll_line
sample_blue='--sample-blue' in sys.argv or classic_text
outlined='--outlines' in sys.argv or sample_blue
framed='--frames' in sys.argv or outlined
out=ROOT/('SD200W_SAIV_OSU107_Blue_ScrollLine.exe' if scroll_line else 'SD200W_SAIV_OSU107_Blue_ClassicText.exe' if classic_text else 'SD200W_SAIV_OSU107_Blue_Custom.exe' if sample_blue else 'SD200W_SAIV_OSU107_Blue_Outlines.exe' if outlined else 'SD200W_SAIV_OSU107_Blue_Frames.exe' if framed else 'SD200W_SAIV_OSU107_Blue.exe')
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='82ef2786a59cd4d89f82b47102bfb71652a1d49d8b58a582753114ba180421f1'
p=pefile.PE(data=original);b=bytearray(original)
t=ast.parse((W/'remove_phone_buttons.py').read_text())
exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
def string(s):return b'\x06'+bytes([len(s)])+s.encode('ascii')
def color(s):
 r,g,bl=bytes.fromhex(s)
 return b'\x04'+struct.pack('<I',r|(g<<8)|(bl<<16))
background=color('EAF1F8');panel=color('DCE8F5');ink=color('20364F');paper=color('F8FBFF')
if sample_blue:panel=color('508CC6')
payload=bytearray();changes=[];rva=p.OPTIONAL_HEADER.SizeOfImage
resources=[(str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries for l in n.directory.entries]
for name,res in resources:
 blob=bytes(p.get_data(res.OffsetToData,res.Size))
 if not blob.startswith(b'TPF0'):continue
 nodes=DfmReader(blob).parse();edits=[];report=[]
 for node,(cls,props,end) in nodes.items():
  vals={k:blob[v:e] for k,s,v,e in props};new={}
  for k,val in vals.items():
   if k.endswith('Font.Name'):
    if val in [string(s) for s in ('Arial','MS Sans Serif','Tahoma')]:new[k]=string('Segoe UI')
    elif val==string('Fixedsys'):new[k]=string('Consolas')
   if k=='Color' and val==b'\x07\x09clBtnFace':new[k]=background
  if node==next(iter(nodes)):
   new['Color']=background
   new['Font.Name']=string('Segoe UI')
  if name=='TFORM1':
   if cls=='TPanel':
    new['Color']=paper if node=='Panel3' else panel if node in ('SpeedPanel','Panel2') else background
    new['BevelOuter']=b'\x07\x06bvNone'
    if (framed and node in ('SpeedPanel','Panel2')) or (outlined and node=='Panel3'):
     new['BorderStyle']=b'\x07\x08bsSingle'
   if node in ('PaintBoxTerm','memComm'):
    new.update({'Color':paper,'Font.Name':string('Consolas'),'Font.Color':ink})
    if classic_text:
     new['Font.Name']=string('Fixedsys')
     new['Font.Color']=color('000000')
   if cls=='TSpeedButton' and node.startswith('sbtn'):new['Flat']=b'\x08' if outlined else b'\x09'
  if not new:continue
  for k,s,v,e in props:
   if k in new:edits.append((s,e,b''))
  edits.append((end,end,b''.join(bytes([len(k)])+k.encode()+v for k,v in new.items())))
  report.append(dict(component=node,properties=list(new)))
 if scroll_line and name=='TFORM1':
  def short(s):return bytes([len(s)])+s.encode()
  def integer(n):return b'\x03'+struct.pack('<h',n)
  props={'Left':integer(617),'Top':integer(0),'Width':integer(1),'Height':integer(435),
         'Anchors':b'\x0b\x05akTop\x07akRight\x08akBottom\x00',
         'Brush.Color':color('000000'),'Pen.Color':color('000000')}
  shape=short('TShape')+short('TerminalScrollDivider')+b''.join(short(k)+v for k,v in props.items())+b'\0\0'
  insertion=nodes['Panel3'][2]+1
  edits.append((insertion,insertion,shape))
 modified=blob
 for start,end,val in sorted(edits,reverse=True):modified=modified[:start]+val+modified[end:]
 after=DfmReader(modified).parse()
 for node,(cls,props,end) in nodes.items():
  before={k:blob[v:e] for k,s,v,e in props};updated={k:modified[v:e] for k,s,v,e in after[node][1]}
  # All wiring, data and geometry are preserved.
  for k,value in before.items():
   if k.startswith('On') or k in ('Left','Top','Width','Height','Visible','Enabled','Caption','Glyph.Data'):assert updated[k]==value,(name,node,k)
 if modified==blob:continue
 payload.extend(bytes((-len(payload))%4));offset=len(payload);payload.extend(modified)
 struct.pack_into('<II',b,res.get_file_offset(),rva+offset,len(modified))
 changes.append(dict(form=name,components=report))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1]
assert last.Name.rstrip(b'\0')==b'.rows'
raw=last.PointerToRawData+rva-last.VirtualAddress
assert raw>=len(b)
size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload))
struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfInitializedData'),p.OPTIONAL_HEADER.SizeOfInitializedData+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
report=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),forms=len(changes),changes=changes)
(W/('blue_scroll_line_manifest.json' if scroll_line else 'blue_classic_text_manifest.json' if classic_text else 'blue_custom_manifest.json' if sample_blue else 'blue_outlines_manifest.json' if outlined else 'blue_frames_manifest.json' if framed else 'blue_look_manifest.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='changes'},indent=2))
