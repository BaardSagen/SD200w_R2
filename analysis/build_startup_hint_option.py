from pathlib import Path
import pefile,subprocess,hashlib,struct,json,ast
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_v1.0.8_StartupHint_Sept2026.exe';out=ROOT/'SD200W_SAIV_v1.0.9_StartupOption_Sept2026.exe'
original=source.read_bytes();expected='450ebde32a2ca79331ed6ee1434a38e0f32bbf946554e209477084cb8a1c0550';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x29a000
hint=json.loads((W/'startup_wake_hint_manifest.json').read_text());assert hint['sha256']==expected
hint_state=hint['rva']+hint['symbols']['state'];hint_callback=hint['rva']+hint['symbols']['timer_callback']
subprocess.run(['as','--32','--defsym',f'HINT_STATE={hint_state}','--defsym',f'HINT_CALLBACK={hint_callback}','-o',str(W/'startup_hint_option.o'),str(W/'startup_hint_option.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'startup_hint_option.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'startup_hint_option.o'),str(W/'startup_hint_option.bin')],check=True)
payload=(W/'startup_hint_option.bin').read_bytes();symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'startup_hint_option.o')],text=True).splitlines() if len(t:=line.split())==3}
allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def patch(va,old,new):off=p.get_offset_from_rva(va-0x400000);assert b[off:off+len(old)]==old,(hex(va),b[off:off+len(old)].hex());put(off,new)
patch(0x595ee2,bytes.fromhex('ff53088b55fc'),b'\xe8'+struct.pack('<i',0x400000+rva-0x595ee7)+b'\x90')
patch(0x5140c9,bytes.fromhex('8b45fc8b8000030000'),b'\xe8'+struct.pack('<i',0x400000+rva+symbols['write_option']-0x5140ce)+b'\x90'*4)
patch(0x5131bc,bytes.fromhex('558becb909000000'),b'\xe9'+struct.pack('<i',0x400000+rva+symbols['setup_show']-0x5131c1)+b'\x90'*3)
# Redirect only the deferred startup hint callback; no new timer is created.
start_bytes=p.get_data(hint['rva'],hint['symbols']['receive']);needle=bytes.fromhex('8d87')+struct.pack('<I',hint_callback);assert start_bytes.count(needle)==1
callback_offset=start_bytes.index(needle)+2;put(p.get_offset_from_rva(hint['rva']+callback_offset),struct.pack('<I',rva+symbols['timer_gate']))
for block in p.DIRECTORY_ENTRY_BASERELOC:
 for e in block.entries:
  assert not (e.type and any(a<=e.rva<a+n for a,n in [(0x195ee2,6),(0x1140c9,9),(0x1131bc,8),(hint['rva']+callback_offset,4)]))
entries=[(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
for kind,name,e in entries:
 if (kind==10 and name=='TABOUTBOXNAV') or kind==16:
  data=bytearray(p.get_data(e.OffsetToData,e.Size));old=('1.0.8 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');new=('1.0.9 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');assert old in data;data=data.replace(old,new)
  if kind==16:
   start=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,start+8,0x10000,0x90000,0x10000,0x90000)
  put(p.get_offset_from_rva(e.OffsetToData),data)
# Add an owned checkbox without changing form instance layout or existing fields.
t=ast.parse((W/'remove_phone_buttons.py').read_text());exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
res=next(e for kind,name,e in entries if kind==10 and name=='TCOMMPARAMDLG');blob=p.get_data(res.OffsetToData,res.Size);nodes=DfmReader(blob).parse()
def short(s):return bytes([len(s)])+s.encode('ascii')
def prop(k,v):return short(k)+v
def integer(n):return b'\x03'+struct.pack('<h',n)
child=short('TCheckBox')+short('cbStartupText')
for k,n in [('Left',16),('Top',330),('Width',177),('Height',17),('TabOrder',4)]:child+=prop(k,integer(n))
child+=prop('Caption',b'\x06'+short('Show startup text'))+prop('Checked',b'\x09')+prop('State',b'\x07'+short('cbChecked'))+b'\0\0'
insert=nodes['TabSheet1'][2]+1;modified=blob[:insert]+child+blob[insert:];after=DfmReader(modified).parse();assert after['cbStartupText'][0]=='TCheckBox' and len(after)==len(nodes)+1
payload+=bytes((-len(payload))%4);resource_rva=rva+len(payload);payload+=modified;put(res.get_file_offset(),struct.pack('<II',resource_rva,len(modified)))
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original))
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum();assert source.read_bytes()==original
manifest=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols,ini_section="Comm",ini_key="ShowStartupText",default_enabled=True,resource_rva=resource_rva,validation='Pending emulator and GUI tests')
(W/'startup_hint_option_manifest.json').write_text(json.dumps(manifest,indent=2));print(out.name,manifest['sha256'])
