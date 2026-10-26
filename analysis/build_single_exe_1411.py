"""Manual firmware updater for SAIV110 / OSU107. Preserve 1.4.10 and all native code."""
from pathlib import Path
import ast,hashlib,struct,subprocess,json,pefile,sys
R=Path(__file__).resolve().parent.parent;W=R/'analysis/single1411';W.mkdir(exist_ok=True)
SRC=R/'analysis/reference/sit_import_v1411'
source=R/'analysis/single146/SAIV_IT_Runtime.exe';dll=R/'SIT_Import151.dll';expected='3ca033ad72ef28635e1eeeeff224e4c3340947302f8c07b135e6ed06043c8f69'
# Keep the generated 1.4.10 guide unchanged.
# Model DLL and offline guide; preserve instrument runtime and installer.
previous=json.loads((R/'analysis/single_exe_141_manifest.json').read_text())
original=source.read_bytes();assert hashlib.sha256(original).hexdigest()==expected
helper=W/'SIT_Update.exe';helper.write_bytes((R/'analysis/single141/SIT_Update.exe').read_bytes());assert hashlib.sha256(helper.read_bytes()).hexdigest()==previous['helper_sha256']
subprocess.run(['g++','-std=c++11','-O2','-shared','-static-libgcc','-static-libstdc++','-Wl,--kill-at','-o',str(dll),str(SRC/'sit_import.cpp'),str(SRC/'native_call.s'),str(SRC/'vendor/gsw/gsw_oceanographic_toolbox.c'),str(SRC/'vendor/gsw/gsw_saar.c'),'-lcomctl32','-lcomdlg32','-lgdi32','-luser32','-lshell32','-lole32','-ladvapi32','-lwininet','-lsetupapi','-lcfgmgr32'],check=True)
p=pefile.PE(data=original);b=bytearray(original);resource_ranges=[]
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;data=bytearray(p.get_data(e.OffsetToData,e.Size));enc='utf-16le' if k.id==16 else 'ascii';data=data.replace('1.4.6 Sept.2026'.encode(enc),'1.4.11 Sept2026'.encode(enc))
    assert len(data)==e.Size, 'Resource replacement must preserve its byte length'
    if k.id==16:
     pos=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,pos+8,0x10004,0xb0000,0x10004,0xb0000)
    off=p.get_offset_from_rva(e.OffsetToData);b[off:off+len(data)]=data;resource_ranges.append((off,len(data)))
assert b.count(b'SIT_Import146.dll')==4;b=b.replace(b'SIT_Import146.dll',b'SIT_Import151.dll')
assert pefile.PE(data=bytes(b)).get_data(0x10a000,0x3000)==p.get_data(0x10a000,0x3000)
# Earlier patches relocated resources into .rows, which is also executable.
# Compare the entire file after masking only About/version resources and DLL names.
normalized=bytearray(b.replace(b'SIT_Import151.dll',b'SIT_Import146.dll'))
for off,size in resource_ranges:normalized[off:off+size]=original[off:off+size]
assert normalized==original,'Unexpected runtime change outside version/About/DLL references'
from patch_firmware_quiet import patch_firmware_quiet
b=patch_firmware_quiet(b)
for name in ['launcher.cpp','launcher.manifest']:
 (W/name).write_text(((R/'sit_update/launcher141.cpp') if name=='launcher.cpp' else (R/'analysis/reference/sit_single_v137'/name)).read_text().replace('1.3.7','1.4.11').replace('SIT_Import141.dll','SIT_Import151.dll'))
rp=pefile.PE(data=bytes(b));struct.pack_into('<I',b,rp.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),rp.generate_checksum())
runtime=W/'SAIV_IT_Runtime.exe';runtime.write_bytes(b)
rc='''#include <windows.h>
101 RCDATA "RUNTIME"
102 RCDATA "DLL"
103 RCDATA "HELPER"
104 RCDATA "MINIZLICENSE"
MAINICON ICON "ICON"
1 VERSIONINFO
FILEVERSION 1,4,11,0
PRODUCTVERSION 1,4,11,0
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
   VALUE "FileVersion", "1.4.11 Sept.2026"
   VALUE "ProductName", "SAIV Instrument Terminal"
   VALUE "ProductVersion", "1.4.11 Sept.2026"
   VALUE "OriginalFilename", "SAIV_Instrument_Terminal_v1.4.11_Sept2026.exe"
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
out=R/'SAIV_Instrument_Terminal_v1.4.11_Sept2026.exe'
tag='1.4.11_'+hashlib.sha256(b+dll.read_bytes()+helper.read_bytes()).hexdigest()[:12]
(W/'bundle_config.h').write_text('#define SIT_CACHE_TAG L\"'+tag+'\"\n')
subprocess.run(['g++','-std=c++11','-O2','-mwindows','-static','-static-libgcc','-static-libstdc++',str(W/'launcher.cpp'),str(W/'bundle.o'),'-lole32','-lshell32','-o',str(out)],check=True)
q=pefile.PE(str(out));deps=[i.dll.decode() for i in q.DIRECTORY_ENTRY_IMPORT];assert not any('libgcc' in x or 'libstdc' in x for x in deps)
for key,data in [(101,bytes(b)),(102,dll.read_bytes()),(103,helper.read_bytes())]:
 e=next(l.data.struct for k in q.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if n.id==key for l in n.directory.entries);assert q.get_data(e.OffsetToData,e.Size)==data
m=dict(cache_tag=tag,source=source.relative_to(R).as_posix(),source_sha256=expected,output=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),runtime_sha256=hashlib.sha256(b).hexdigest(),dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),dependencies=deps,bytes=out.stat().st_size)
(R/'analysis/single_exe_1411_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))
