"""UI-only 1.3.8 release from the preserved 1.3.7 runtime and DLL."""
from pathlib import Path
import ast,hashlib,struct,subprocess,json,pefile
R=Path(__file__).resolve().parent.parent;W=R/'analysis/single138';W.mkdir(exist_ok=True)
source=R/'analysis/single137/SAIV_IT_Runtime.exe';dll=R/'SIT_Import137.dll';expected='976f4e2555473ed31fa72034088a6e84b3caa104169d7fffa88d9ee9c2a38cfc'
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()==expected
assert hashlib.sha256(dll.read_bytes()).hexdigest()=='1d004689119c82901df9bf2a412ff7683ae4a09ac5c371872aba7c85c727e457'
p=pefile.PE(data=original);b=bytearray(original);allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
t=ast.parse((R/'analysis/remove_phone_buttons.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'reader','exec'))
short=lambda s:bytes([len(s)])+s.encode('ascii')
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   e=l.data.struct;data=p.get_data(e.OffsetToData,e.Size)
   if k.id==10 and str(n.name)=='TFORM1':
    nodes=DfmReader(data).parse();edits=[]
    changes={'btnPhone':{'Caption':b'\x06'+short('D&etect')},'btnLogReadout':{'Visible':b'\x08','TabStop':b'\x08'}}
    for name,props in changes.items():
     for key,st,v,z in nodes[name][1]:
      if key in props:edits.append((st,z,b''))
     edits.append((nodes[name][2],nodes[name][2],b''.join(short(key)+value for key,value in props.items())))
    changed=data
    for st,z,value in sorted(edits,reverse=True):changed=changed[:st]+value+changed[z:]
    updated=DfmReader(changed).parse();assert nodes.keys()==updated.keys()
    for name in nodes:
     before={k:data[v:z] for k,st,v,z in nodes[name][1]};after={k:changed[v:z] for k,st,v,z in updated[name][1]};before.update(changes.get(name,{}));assert before==after,name
    assert b'\x06\x09&Download' in changed
    last=p.sections[-1];raw=len(b);addr=last.VirtualAddress+raw-last.PointerToRawData
    b.extend(changed);align=lambda n,a:(n+a-1)//a*a
    b.extend(bytes(align(len(b),p.OPTIONAL_HEADER.FileAlignment)-len(b)))
    put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',addr-last.VirtualAddress+len(changed)))
    put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',len(b)-last.PointerToRawData))
    put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(addr+len(changed),p.OPTIONAL_HEADER.SectionAlignment)))
    put(e.get_file_offset(),struct.pack('<II',addr,len(changed)))
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    enc='utf-16le' if k.id==16 else 'ascii';changed=data.replace('1.3.7 Sept.2026'.encode(enc),'1.3.8 Sept.2026'.encode(enc));assert changed!=data
    if k.id==16:
     changed=bytearray(changed);pos=changed.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',changed,pos+8,0x10003,0x80000,0x10003,0x80000)
    put(p.get_offset_from_rva(e.OffsetToData),changed)
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(v==b[i] or i in allowed for i,v in enumerate(original))
assert pefile.PE(data=bytes(b)).verify_checksum()
for name in ['launcher.cpp','launcher.manifest']:
 (W/name).write_text((R/'analysis/reference/sit_single_v137'/name).read_text().replace('1.3.7','1.3.8'))
runtime=W/'SAIV_IT_Runtime.exe';runtime.write_bytes(b)
rc='''#include <windows.h>
101 RCDATA "RUNTIME"
102 RCDATA "DLL"
MAINICON ICON "ICON"
1 VERSIONINFO
FILEVERSION 1,3,8,0
PRODUCTVERSION 1,3,8,0
FILEFLAGSMASK 0x3fL
FILEFLAGS 0
FILEOS 0x40004L
FILETYPE 1
BEGIN
 BLOCK "StringFileInfo"
 BEGIN
  BLOCK "040904b0"
  BEGIN
   VALUE "CompanyName", "SAIV"
   VALUE "FileDescription", "SAIV Instrument Terminal"
   VALUE "FileVersion", "1.3.8 Sept.2026"
   VALUE "ProductName", "SAIV Instrument Terminal"
   VALUE "ProductVersion", "1.3.8 Sept.2026"
   VALUE "OriginalFilename", "SAIV_Instrument_Terminal_v1.3.8_Sept2026.exe"
  END
 END
 BLOCK "VarFileInfo"
 BEGIN
  VALUE "Translation", 0x409, 1200
 END
END
'''.replace('RUNTIME',runtime.as_posix()).replace('DLL',dll.as_posix())
# Substitute only the quoted icon path, not the ICON resource keyword.
rc=rc.replace('"ICON"','"'+(R/'icon/ctd_in_Cage.ico').as_posix()+'"')
rc+='\n1 24 \"'+(W/'launcher.manifest').as_posix()+'\"\n'
(W/'bundle.rc').write_text(rc)
subprocess.run(['windres','-i',str(W/'bundle.rc'),'-o',str(W/'bundle.o')],check=True)
out=R/'SAIV_Instrument_Terminal_v1.3.8_Sept2026.exe'
tag='1.3.8_'+hashlib.sha256(b+dll.read_bytes()).hexdigest()[:12]
(W/'bundle_config.h').write_text('#define SIT_CACHE_TAG L\"'+tag+'\"\n')
subprocess.run(['g++','-std=c++11','-O2','-mwindows','-static','-static-libgcc','-static-libstdc++',str(W/'launcher.cpp'),str(W/'bundle.o'),'-lole32','-lshell32','-o',str(out)],check=True)
q=pefile.PE(str(out));deps=[i.dll.decode() for i in q.DIRECTORY_ENTRY_IMPORT];assert not any('libgcc' in x or 'libstdc' in x for x in deps)
for key,data in [(101,bytes(b)),(102,dll.read_bytes())]:
 e=next(l.data.struct for k in q.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if n.id==key for l in n.directory.entries);assert q.get_data(e.OffsetToData,e.Size)==data
m=dict(cache_tag=tag,source=source.relative_to(R).as_posix(),source_sha256=expected,output=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),runtime_sha256=hashlib.sha256(b).hexdigest(),dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),dependencies=deps,bytes=out.stat().st_size)
(R/'analysis/single_exe_138_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
