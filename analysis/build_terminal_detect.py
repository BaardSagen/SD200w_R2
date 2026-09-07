from pathlib import Path
import ast, hashlib, json, struct, subprocess
import pefile
ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_History.exe'
output=ROOT/'SD200W_SAIV_OSU107_Detect.exe'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=='0cd67dc3a0811be364e301a0a61e28681241713f999066862fbd9a42cfbab959'
p=pefile.PE(data=original)
tree=ast.parse((WORK/'remove_phone_buttons.py').read_text())
exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
resources={str(name.name):lang.data.struct for kind in p.DIRECTORY_ENTRY_RESOURCE.entries if kind.id==10
           for name in kind.directory.entries for lang in name.directory.entries}
main=resources['TFORM1']; setup=resources['TCOMMPARAMDLG']
blob=p.get_data(main.OffsetToData,main.Size); setup_blob=p.get_data(setup.OffsetToData,setup.Size)
nodes=DfmReader(blob).parse(); setup_nodes=DfmReader(setup_blob).parse()
def values(data,node): return {key:data[v:e] for key,s,v,e in node[1]}
detect_values=values(setup_blob,setup_nodes['DetectBtn'])
target=nodes['btnPhone']; assert target[0]=='TSpeedButton'
changes=[]
new_props={'Caption':b'\x06\x07&Detect','Visible':b'\x09','Enabled':b'\x09',
           'OnClick':b'\x07\x0dbtnPhoneClick','Glyph.Data':detect_values['Glyph.Data'],
           'NumGlyphs':detect_values.get('NumGlyphs',b'\x02\x02')}
for key,s,v,e in target[1]:
 if key in new_props: changes.append((s,e,b''))
addition=b''.join(bytes([len(k)])+k.encode()+v for k,v in new_props.items())
changes.append((target[2],target[2],addition))
modified=blob
for s,e,value in sorted(changes,reverse=True): modified=modified[:s]+value+modified[e:]
new_nodes=DfmReader(modified).parse()
for name,node in nodes.items():
 expected=values(blob,node)
 if name=='btnPhone': expected.update(new_props)
 assert expected==values(modified,new_nodes[name]),name
assert values(blob,nodes['btnPhone'])['Top']==b'\x03\xb0\x00'
b=bytearray(original)
resource_off=p.get_offset_from_rva(main.OffsetToData)
assert b[resource_off+len(blob):resource_off+len(modified)]==bytes(len(modified)-len(blob))
b[resource_off:resource_off+len(modified)]=modified
struct.pack_into('<I',b,main.get_field_absolute_offset('Size'),len(modified))
subprocess.run(['as','--32','-o',str(WORK/'terminal_detect.o'),str(WORK/'terminal_detect.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(WORK/'terminal_detect.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(WORK/'terminal_detect.o'),str(WORK/'terminal_detect.bin')],check=True)
payload=(WORK/'terminal_detect.bin').read_bytes()
symbols={}
for line in subprocess.check_output(['nm','-n',str(WORK/'terminal_detect.o')],text=True).splitlines():
 t=line.split()
 if len(t)==3:symbols[t[2]]=int(t[0],16)
rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x23f000
patches=[]
for va,expected,label,opcode in [(0x5a54a4,'558becb904000000','entry',0xe9),(0x5a10c2,'ff92d8000000','modal_bridge',0xe8),(0x5132ed,'ff92b0000000','setup_focus',0xe8)]:
 off=p.get_offset_from_rva(va-0x400000)
 # The entire prologue is replaced for the retired Call handler; it is never resumed.
 assert b[off:off+len(bytes.fromhex(expected))]==bytes.fromhex(expected),(hex(va),b[off:off+8].hex())
 size=len(bytes.fromhex(expected))
 assert not any(e.type and va-0x400000<=e.rva<va-0x400000+size for block in p.DIRECTORY_ENTRY_BASERELOC for e in block.entries)
 b[off:off+size]=bytes([opcode])+struct.pack('<i',0x400000+rva+symbols[label]-va-5)+b'\x90'*(size-5)
 patches.append(dict(address=hex(va),target=label))
def align(n,a):return (n+a-1)//a*a
header=p.sections[-1].get_file_offset()+40
assert header+40<=p.OPTIONAL_HEADER.SizeOfHeaders and b[header:header+40]==bytes(40)
raw=align(len(b),p.OPTIONAL_HEADER.FileAlignment);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<8sIIIIIIHHI',b,header,b'.detect',len(payload),rva,size,raw,0,0,0,0,0xe0000060)
struct.pack_into('<H',b,p.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(p.sections)+1)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
output.write_bytes(b)
assert pefile.PE(str(output)).verify_checksum()
assert source.read_bytes()==original
report=dict(output=output.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols,patches=patches,
            behavior='Detect under Print uses existing search dialog, commits only on acceptance; Setup Detect remains unchanged.')
(WORK/'terminal_detect_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
