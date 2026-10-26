"""Validate exact release contents and the limited legacy-runtime patch surface."""
from pathlib import Path
import hashlib,json,struct,pefile
R=Path(__file__).resolve().parent.parent
old=(R/'analysis/single1411/SAIV_IT_Runtime.exe').read_bytes()
new=(R/'analysis/single1412/SAIV_IT_Runtime.exe').read_bytes()
p=pefile.PE(data=old);q=pefile.PE(data=new)
normalized=bytearray(new[:len(old)].replace(b'SIT_Import152.dll',b'SIT_Import151.dll'))
allowed=[]
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;allowed.append((p.get_offset_from_rva(e.OffsetToData),e.Size))
allowed.append((p.get_offset_from_rva(0x1a593c),8))
for off in [p.sections[-1].get_field_absolute_offset('Misc_VirtualSize'),p.sections[-1].get_field_absolute_offset('SizeOfRawData'),p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')]:allowed.append((off,4))
for off,size in allowed:normalized[off:off+size]=old[off:off+size]
assert bytes(normalized)==old,'Unexpected existing-runtime change'
assert q.verify_checksum()
assert (q.VS_FIXEDFILEINFO[0].FileVersionMS,q.VS_FIXEDFILEINFO[0].FileVersionLS)==(0x10004,0xc0000)
m=json.loads((R/'analysis/single_exe_1412_manifest.json').read_text());exe=R/m['output'];outer=pefile.PE(str(exe))
assert hashlib.sha256(exe.read_bytes()).hexdigest()==m['sha256']
assert not outer.OPTIONAL_HEADER.DATA_DIRECTORY[4].Size,'Unexpected certificate'
expected={101:new,102:(R/'SIT_Import152.dll').read_bytes(),103:(R/'analysis/single1411/SIT_Update.exe').read_bytes()}
for k in outer.DIRECTORY_ENTRY_RESOURCE.entries:
 if k.id==10:
  for n in k.directory.entries:
   if n.id in expected:
    for l in n.directory.entries:
     e=l.data.struct;assert outer.get_data(e.OffsetToData,e.Size)==expected.pop(n.id)
assert not expected
prior=json.loads((R/'analysis/single_exe_1411_manifest.json').read_text())
assert hashlib.sha256((R/prior['output']).read_bytes()).hexdigest()==prior['sha256']
for name in ['conversions.inc','logger.h','model_conversions.inc','science.h','legacy_convert.h','firmware_ui.inc','firmware_windows.inc','firmware_protocol.h']:
 assert (R/'sit_import'/name).read_bytes()==(R/'analysis/reference/sit_import_v1411'/name).read_bytes(),name
result=dict(passed=True,build=m,existing_runtime_changes_limited_to=['Convert dispatch','DLL name','About/version','PE size/checksum fields'],formula_and_firmware_sources_unchanged=True,embedded_components_exact=True,previous_release_unchanged=True,signature='unsigned; signing service pending')
(R/'analysis/batch1412_static_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS exact embedded components, runtime patch boundaries, unchanged calculations/firmware, preserved 1.4.11')
