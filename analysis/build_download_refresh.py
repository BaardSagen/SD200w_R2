from pathlib import Path
import ast,hashlib,json,struct,subprocess,pefile
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_OSU107_SelectInstrument.exe';out=ROOT/'SD200W_SAIV_OSU107_Refresh.exe'
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()=='f726c144d92c82d9ae89e92efcdf49deb0e523d23805370fd4b1f6125dc6c802'
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x285000
subprocess.run(['as','--32','-o',str(W/'download_refresh.o'),str(W/'download_refresh.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'download_refresh.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'download_refresh.o'),str(W/'download_refresh.bin')],check=True)
payload=bytearray((W/'download_refresh.bin').read_bytes());code_size=len(payload)
symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'download_refresh.o')],text=True).splitlines() if len(t:=line.split())==3}
old=json.loads((W/'patch_manifest.json').read_text())
for record in old['changes']:
 va=int(record['address'],16);off=p.get_offset_from_rva(va-0x400000)
 assert b[off:off+len(bytes.fromhex(record['patched']))]==bytes.fromhex(record['patched'])
 b[off:off+5]=b'\xe9'+struct.pack('<i',0x400000+rva+symbols[record['label']]-va-5)
t=ast.parse((W/'remove_phone_buttons.py').read_text());exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
res=next(l.data.struct for k in p.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if str(n.name)=='TFORM1' for l in n.directory.entries)
blob=p.get_data(res.OffsetToData,res.Size);nodes=DfmReader(blob).parse();edits=[]
vals={n:{k:blob[v:e] for k,s,v,e in nodes[n][1]} for n in ('btnPhone','btnCommSetup')}
for name,other in [('btnPhone','btnCommSetup'),('btnCommSetup','btnPhone')]:
 for k,s,v,e in nodes[name][1]:
  if k=='Top':edits.append((v,e,vals[other]['Top']))
modified=blob
for s,e,v in sorted(edits,reverse=True):modified=modified[:s]+v+modified[e:]
after=DfmReader(modified).parse()
for name,(cl,props,end) in nodes.items():
 actual={k:modified[v:e] for k,s,v,e in after[name][1]};expected={k:blob[v:e] for k,s,v,e in props}
 if name in vals:expected['Top']=vals['btnPhone' if name=='btnCommSetup' else 'btnCommSetup']['Top']
 assert actual==expected,name
payload.extend(bytes((-len(payload))%4));resource_rva=rva+len(payload);payload.extend(modified)
struct.pack_into('<II',b,res.get_file_offset(),resource_rva,len(modified))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
for field,value in [('Misc_VirtualSize',rva-last.VirtualAddress+len(payload)),('SizeOfRawData',rva-last.VirtualAddress+size),('Characteristics',last.Characteristics|0x80000000)]:struct.pack_into('<I',b,last.get_field_absolute_offset(field),value)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
m=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),section_rva=rva,section_size=code_size,symbols=symbols)
(W/'refresh_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({k:v for k,v in m.items() if k!='symbols'},indent=2))
