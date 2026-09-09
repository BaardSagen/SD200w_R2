"""Instrument settings release from preserved 1.3.8 runtime."""
from pathlib import Path
import ast,hashlib,struct,subprocess,json,pefile
R=Path(__file__).resolve().parent.parent;W=R/'analysis/single143';W.mkdir(exist_ok=True)
source=R/'analysis/single142/SAIV_IT_Runtime.exe';dll=R/'SIT_Import143.dll';expected='90517b7846615b14eb3c1ab19e575222c4c972131f8f13d14fc215a44d4f487f'
# Update-dialog hint; preserve runtime and installer from the prior release.
previous=json.loads((R/'analysis/single_exe_141_manifest.json').read_text())
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()==expected
helper=W/'SIT_Update.exe';helper.write_bytes((R/'analysis/single141/SIT_Update.exe').read_bytes());assert hashlib.sha256(helper.read_bytes()).hexdigest()==previous['helper_sha256']
subprocess.run(['g++','-std=c++11','-O2','-shared','-static-libgcc','-static-libstdc++','-Wl,--kill-at','-o',str(dll),str(R/'sit_import/sit_import.cpp'),str(R/'sit_import/native_call.s'),'-lcomctl32','-lcomdlg32','-lgdi32','-luser32','-lshell32','-lole32','-ladvapi32','-lwininet'],check=True)
p=pefile.PE(data=original);b=bytearray(original)
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;data=bytearray(p.get_data(e.OffsetToData,e.Size));enc='utf-16le' if k.id==16 else 'ascii';data=data.replace('1.4.2 Sept.2026'.encode(enc),'1.4.3 Sept.2026'.encode(enc))
    if k.id==16:
     pos=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,pos+8,0x10004,0x30000,0x10004,0x30000)
    off=p.get_offset_from_rva(e.OffsetToData);b[off:off+len(data)]=data
assert b.count(b'SIT_Import142.dll')==4;b=b.replace(b'SIT_Import142.dll',b'SIT_Import143.dll')
assert pefile.PE(data=bytes(b)).get_data(0x10a000,0x3000)==p.get_data(0x10a000,0x3000)
for name in ['launcher.cpp','launcher.manifest']:
 (W/name).write_text(((R/'sit_update/launcher141.cpp') if name=='launcher.cpp' else (R/'analysis/reference/sit_single_v137'/name)).read_text().replace('1.3.7','1.4.3').replace('SIT_Import141.dll','SIT_Import143.dll'))
rp=pefile.PE(data=bytes(b));struct.pack_into('<I',b,rp.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),rp.generate_checksum())
runtime=W/'SAIV_IT_Runtime.exe';runtime.write_bytes(b)
rc='''#include <windows.h>
101 RCDATA "RUNTIME"
102 RCDATA "DLL"
103 RCDATA "HELPER"
104 RCDATA "MINIZLICENSE"
MAINICON ICON "ICON"
1 VERSIONINFO
FILEVERSION 1,4,3,0
PRODUCTVERSION 1,4,3,0
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
   VALUE "FileVersion", "1.4.3 Sept.2026"
   VALUE "ProductName", "SAIV Instrument Terminal"
   VALUE "ProductVersion", "1.4.3 Sept.2026"
   VALUE "OriginalFilename", "SAIV_Instrument_Terminal_v1.4.3_Sept2026.exe"
  END
 END
 BLOCK "VarFileInfo"
 BEGIN
  VALUE "Translation", 0x409, 1200
 END
END
'''.replace('RUNTIME',runtime.as_posix()).replace('DLL',dll.as_posix()).replace('HELPER',helper.as_posix()).replace('MINIZLICENSE',(R/'sit_update/miniz/LICENSE').as_posix())
# Substitute only the quoted icon path, not the ICON resource keyword.
rc=rc.replace('"ICON"','"'+(R/'icon/ctd_in_Cage.ico').as_posix()+'"')
rc+='\n1 24 \"'+(W/'launcher.manifest').as_posix()+'\"\n'
(W/'bundle.rc').write_text(rc)
subprocess.run(['windres','-i',str(W/'bundle.rc'),'-o',str(W/'bundle.o')],check=True)
out=R/'SAIV_Instrument_Terminal_v1.4.3_Sept2026.exe'
tag='1.4.3_'+hashlib.sha256(b+dll.read_bytes()+helper.read_bytes()).hexdigest()[:12]
(W/'bundle_config.h').write_text('#define SIT_CACHE_TAG L\"'+tag+'\"\n')
subprocess.run(['g++','-std=c++11','-O2','-mwindows','-static','-static-libgcc','-static-libstdc++',str(W/'launcher.cpp'),str(W/'bundle.o'),'-lole32','-lshell32','-o',str(out)],check=True)
q=pefile.PE(str(out));deps=[i.dll.decode() for i in q.DIRECTORY_ENTRY_IMPORT];assert not any('libgcc' in x or 'libstdc' in x for x in deps)
for key,data in [(101,bytes(b)),(102,dll.read_bytes()),(103,helper.read_bytes())]:
 e=next(l.data.struct for k in q.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if n.id==key for l in n.directory.entries);assert q.get_data(e.OffsetToData,e.Size)==data
m=dict(cache_tag=tag,source=source.relative_to(R).as_posix(),source_sha256=expected,output=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),runtime_sha256=hashlib.sha256(b).hexdigest(),dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),dependencies=deps,bytes=out.stat().st_size)
(R/'analysis/single_exe_143_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
