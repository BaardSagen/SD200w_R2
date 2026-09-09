from pathlib import Path
import pefile,hashlib,struct,subprocess,json
R=Path(__file__).resolve().parent.parent;W=R/'analysis/single137';W.mkdir(exist_ok=True)
source=R/'analysis/single136/SAIV_IT_Runtime.exe';dll=R/'SIT_Import137.dll';expected='79541dd7fcb8b4caf2d4bea64751ed740eaeb59bf5656929621127799afc5ca4';assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
subprocess.run(['g++','-std=c++11','-O2','-shared','-static-libgcc','-static-libstdc++','-Wl,--kill-at','-o',str(dll),str(R/'sit_import/sit_import.cpp'),str(R/'sit_import/native_call.s'),'-lcomctl32','-lcomdlg32','-lgdi32','-luser32','-lshell32','-lole32','-ladvapi32'],check=True)
p=pefile.PE(str(source));b=bytearray(source.read_bytes());allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;data=bytearray(p.get_data(e.OffsetToData,e.Size));enc='utf-16le' if k.id==16 else 'ascii';old='1.3.6 Sept.2026'.encode(enc);assert old in data;data=data.replace(old,'1.3.7 Sept.2026'.encode(enc))
    if k.id==16:
     pos=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,pos+8,0x10003,0x70000,0x10003,0x70000)
    put(p.get_offset_from_rva(e.OffsetToData),data)
oldname=b'SIT_Import136.dll';start=0;count=0
while True:
 pos=source.read_bytes().find(oldname,start)
 if pos<0:break
 put(pos,b'SIT_Import137.dll');count+=1;start=pos+len(oldname)
assert count==3
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(v==b[i] or i in allowed for i,v in enumerate(source.read_bytes()));from patch_native137 import patch_native
b=patch_native(b)
assert pefile.PE(data=bytes(b)).get_data(0x10a000,0x3000)==p.get_data(0x10a000,0x3000)
runtime=W/'SAIV_IT_Runtime.exe';runtime.write_bytes(b)
rc='''#include <windows.h>
101 RCDATA "RUNTIME"
102 RCDATA "DLL"
MAINICON ICON "ICON"
1 VERSIONINFO
FILEVERSION 1,3,7,0
PRODUCTVERSION 1,3,7,0
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
   VALUE "FileVersion", "1.3.7 Sept.2026"
   VALUE "ProductName", "SAIV Instrument Terminal"
   VALUE "ProductVersion", "1.3.7 Sept.2026"
   VALUE "OriginalFilename", "SAIV_Instrument_Terminal_v1.3.7_Sept2026.exe"
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
rc+='\n1 24 \"'+(R/'sit_single/launcher.manifest').as_posix()+'\"\n'
(W/'bundle.rc').write_text(rc)
subprocess.run(['windres','-i',str(W/'bundle.rc'),'-o',str(W/'bundle.o')],check=True)
out=R/'SAIV_Instrument_Terminal_v1.3.7_Sept2026.exe'
tag='1.3.7_'+hashlib.sha256(b+dll.read_bytes()).hexdigest()[:12]
(R/'sit_single/bundle_config.h').write_text('#define SIT_CACHE_TAG L\"'+tag+'\"\n')
subprocess.run(['g++','-std=c++11','-O2','-mwindows','-static','-static-libgcc','-static-libstdc++',str(R/'sit_single/launcher.cpp'),str(W/'bundle.o'),'-lole32','-lshell32','-o',str(out)],check=True)
q=pefile.PE(str(out));deps=[i.dll.decode() for i in q.DIRECTORY_ENTRY_IMPORT];assert not any('libgcc' in x or 'libstdc' in x for x in deps)
for key,data in [(101,bytes(b)),(102,dll.read_bytes())]:
 e=next(l.data.struct for k in q.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if n.id==key for l in n.directory.entries);assert q.get_data(e.OffsetToData,e.Size)==data
m=dict(cache_tag=tag,source=source.relative_to(R).as_posix(),source_sha256=expected,output=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),runtime_sha256=hashlib.sha256(b).hexdigest(),dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),dependencies=deps,bytes=out.stat().st_size)
(R/'analysis/single_exe_137_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
