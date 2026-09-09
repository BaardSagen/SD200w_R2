"""Build portable import DLL and hash-bound SIT 1.3.1 executable. No source file is overwritten."""
from pathlib import Path
import ast,hashlib,json,struct,subprocess,pefile
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis';SRC=ROOT/'analysis/reference/sit_import_v131'
source=ROOT/'SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe';out=ROOT/'SAIV_Instrument_Terminal_v1.3.1_Sept2026.exe'
original=source.read_bytes();expected='60f8713bfeda9baffdb690e2bc0c2ff2f4e12516ceb1087b35257ec91b110035';assert hashlib.sha256(original).hexdigest()==expected
subprocess.run(['g++','-std=c++11','-O2','-shared','-static-libgcc','-static-libstdc++','-Wl,--kill-at','-o',str(ROOT/'SIT_Import131.dll'),str(SRC/'sit_import.cpp'),'-lcomctl32','-lcomdlg32','-lgdi32','-luser32','-lshell32','-lole32'],check=True)
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
asm=(SRC/'import_hook_131.s').read_text();asm='.equ PAYLOAD_RVA, %d\n.equ done_jump, %d\n.equ legacy_jump, %d\n'%(rva,0x1a5b39-rva,0x1a5a53-rva)+asm
asm='.equ import_entry_return, %d\n'%(0x1a5944-rva)+asm
(W/'import_hook_generated.s').write_text(asm)
subprocess.run(['as','--32',str(W/'import_hook_generated.s'),'-o',str(W/'import_hook.o')],check=True)
# Link resolves PC-relative jumps to the original image; raw objcopy alone would leave relocations.
subprocess.run(['ld','-m','i386pe','-Ttext','0','--entry','import_hook',str(W/'import_hook.o'),'-o',str(W/'import_hook_linked.exe')],check=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'import_hook_linked.exe'),str(W/'import_hook.bin')],check=True)
payload=bytearray((W/'import_hook.bin').read_bytes())
nm=subprocess.check_output(['nm',str(W/'import_hook.o')],text=True)
merge_offset=int(next(line.split()[0] for line in nm.splitlines() if line.endswith(' T merge_dispatch')),16)
off=p.get_offset_from_rva(0x1a593c);assert b[off:off+8]==bytes.fromhex('558becb906000000')
put(off,b'\xe9'+struct.pack('<i',rva+merge_offset-0x1a593c-5)+b'\x90'*3)
def add(data):payload.extend(bytes((-len(payload))%4));addr=rva+len(payload);payload.extend(data);return addr
at=p.get_offset_from_rva(0x1a5a4a);assert b[at:at+9]==bytes.fromhex('8d55e08b83e8020000');put(at,b'\xe9'+struct.pack('<i',rva-0x1a5a4a-5)+b'\x90'*4)
# Fix both spelling errors in every preserved native logger-refresh message.
old_message=b'Preforming refresh off disks\0';new_message=b'Performing refresh of disks\0'
positions=[];pos=0
while True:
 pos=original.find(old_message,pos)
 if pos<0:break
 positions.append(pos);put(pos,new_message.ljust(len(old_message),b'\0'));pos+=len(old_message)
assert len(positions)==3,positions
# New caption and file filter, retaining the original Burst filter and index behavior.
for va,old,value in [(0x5a5968,0x5a5bd0,'Convert TXT/CSV'),(0x5a5994,0x5a5be8,'CSV/TXT files (*.csv;*.txt)|*.csv;*.txt|Burst Files (*.burst)|*.burst|All files (*.*)|*.*')]:
 off=p.get_offset_from_rva(va-0x400000);assert struct.unpack_from('<I',b,off)[0]==old
 raw=value.encode();addr=add(struct.pack('<iI',-1,len(raw))+raw+b'\0')+8
 put(off,struct.pack('<I',0x400000+addr))
 # Existing absolute-address relocation is retained.
 assert va-0x400000 in {e.rva for block in p.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3}
t=ast.parse((W/'remove_phone_buttons.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'DfmReader','exec'))
# Reuse only the version-resource function, without executing the historical builder.
tree=ast.parse((W/'build_saiv_name.py').read_text(encoding='utf-8-sig'));f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='rebuild_version');code=ast.unparse(f).replace('1.1.3 Sept.2026','1.3.1 Sept.2026').replace('0x10001','0x10002').replace('0x30000','0')
# ast.unparse formats integer constants as decimal.
code=code.replace('65537, 196608, 65537, 196608','65539, 65536, 65539, 65536');TITLE='SAIV Instrument Terminal';exec(code)
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   e=l.data.struct;data=p.get_data(e.OffsetToData,e.Size);updated=None
   if k.id==16:updated=rebuild_version(data)
   elif k.id==10 and str(n.name)=='TABOUTBOXNAV':updated=data.replace(b'1.1.3 Sept.2026',b'1.3.1 Sept.2026')
   elif k.id==10 and str(n.name)=='TFORM1':
    node=DfmReader(data).parse()['mnuImportASCII'];key,st,v,z=next(x for x in node[1] if x[0]=='Caption');caption=b'&Convert TXT/CSV...';updated=data[:v]+b'\x06'+bytes([len(caption)])+caption+data[z:]
    nodes=DfmReader(updated).parse();edits=[]
    for name,top in [('btnLogReadout',152),('btnPrintEcho',184),('btnCommSetup',216)]:
     key,st,v,z=next(x for x in nodes[name][1] if x[0]=='Top');edits.append((v,z,b'\x03'+struct.pack('<h',top)))
    def short(s):raw=s.encode('ascii');return bytes([len(raw)])+raw
    def prop(k,v):return short(k)+v
    button=short('TButton')+short('btnImportCSV')
    for key,value in [('Left',20),('Top',88),('Width',85),('Height',27),('TabOrder',4)]:button+=prop(key,b'\x03'+struct.pack('<h',value))
    button+=prop('Caption',b'\x06'+short('&Convert'))+prop('OnClick',b'\x07'+short('mnuImportASCIIClick'))+b'\0\0'
    merge_button=short('TButton')+short('btnMergeFiles')
    for key,value in [('Left',20),('Top',120),('Width',85),('Height',27),('TabOrder',5)]:merge_button+=prop(key,b'\x03'+struct.pack('<h',value))
    merge_button+=prop('Tag',b'\x04'+struct.pack('<I',0x534d4752))+prop('Caption',b'\x06'+short('&Merge'))+prop('OnClick',b'\x07'+short('mnuImportASCIIClick'))+b'\0\0'
    button+=merge_button
    insertion=nodes['btnDownload'][2]+2
    assert updated[insertion-2:insertion]==b'\0\0'
    edits.append((insertion,insertion,button))
    for st,z,value in sorted(edits,reverse=True):updated=updated[:st]+value+updated[z:]
    assert set(DfmReader(updated).parse())==set(DfmReader(data).parse())|{'btnImportCSV','btnMergeFiles'}
   if updated is not None:put(e.get_file_offset(),struct.pack('<II',add(updated),len(updated)))
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
def align(n,a):return (n+a-1)//a*a
size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(last.get_field_absolute_offset('Characteristics'),struct.pack('<I',last.Characteristics|0xe0000000))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
put(p.OPTIONAL_HEADER.DATA_DIRECTORY[2].get_field_absolute_offset('Size'),struct.pack('<I',rva+len(payload)-p.OPTIONAL_HEADER.DATA_DIRECTORY[2].VirtualAddress))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(v==b[i] or i in allowed for i,v in enumerate(original));out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum()
assert p.get_data(0x10a000,0x3000)==pefile.PE(str(out)).get_data(0x10a000,0x3000)
dll=pefile.PE(str(ROOT/'SIT_Import131.dll'));imports=[x.dll.decode() for x in dll.DIRECTORY_ENTRY_IMPORT];assert not any('libgcc' in x or 'libstdc' in x for x in imports)
manifest=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),dll_sha256=hashlib.sha256((ROOT/'SIT_Import131.dll').read_bytes()).hexdigest(),dll_dependencies=imports,hook_rva=rva,ctd_formula_bytes_unchanged=True,merge_dispatch_rva=rva+merge_offset)
(W/'logger_import_131_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
