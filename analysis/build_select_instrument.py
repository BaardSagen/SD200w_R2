from pathlib import Path
import ast,hashlib,json,struct,subprocess,pefile
ROOT=Path.cwd();W=ROOT/'analysis';source=ROOT/'SD200W_SAIV_OSU107_LoggerDetect.exe';out=ROOT/'SD200W_SAIV_OSU107_SelectInstrument.exe'
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()=='d6b19b035415d159403113bed265f5b530b07819d7ab2aba08e0ad2b1b0c00bf'
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x284000
# Original selection rejects the final valid array index. Change <= to <.
off=p.get_offset_from_rva(0x111baf);assert b[off]==0x7e;b[off]=0x7c
subprocess.run(['as','--32','-o',str(W/'select_instrument.o'),str(W/'select_instrument.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'select_instrument.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'select_instrument.o'),str(W/'select_instrument.bin')],check=True)
payload=bytearray((W/'select_instrument.bin').read_bytes())
# Reuse the retired Aux event for double-click, preserving the relocated method table.
off=p.get_offset_from_rva(0x111c70);assert b[off:off+8]==bytes.fromhex('538bd8ba01000000')
b[off:off+8]=b'\xe9'+struct.pack('<i',rva-0x111c70-5)+b'\x90'*3
assert original[0x11054f-7:0x11054f-3]==struct.pack('<I',0x2d0) # OKBtn field

t=ast.parse((W/'remove_phone_buttons.py').read_text());exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
res=next(l.data.struct for k in p.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if str(n.name)=='TDLGAUTOBAUD' for l in n.directory.entries)
blob=p.get_data(res.OffsetToData,res.Size);nodes=DfmReader(blob).parse();edits=[]
def ident(s):return b'\x07'+bytes([len(s)])+s.encode()
for name in ['btnInstr','btnAux','btnNone','Label3','lbProbes']:
 props=nodes[name][1];new={'Visible':b'\x08'} if name!='lbProbes' else {'OnClick':ident('btnInstrClick'),'OnDblClick':ident('btnAuxClick')}
 if name.startswith('btn'):new['TabStop']=b'\x08'
 for k,s,v,e in props:
  if k in new:edits.append((s,e,b''))
 edits.append((nodes[name][2],nodes[name][2],b''.join(bytes([len(k)])+k.encode()+v for k,v in new.items())))
modified=blob
for s,e,v in sorted(edits,reverse=True):modified=modified[:s]+v+modified[e:]
after=DfmReader(modified).parse()
for name in ['btnInstr','btnAux','btnNone','Label3']:
 assert {k:modified[v:e] for k,s,v,e in after[name][1]}['Visible']==b'\x08'
payload.extend(bytes((-len(payload))%4));resource_rva=rva+len(payload);payload.extend(modified)
struct.pack_into('<II',b,res.get_file_offset(),resource_rva,len(modified))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload))
struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+size)
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=bytes(b)).generate_checksum())
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
m=dict(output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,resource_rva=resource_rva)
(W/'select_instrument_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
