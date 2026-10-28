"""Verify final 1.4.12 naming and unchanged tested 3.1.2 / 3.3.0 functionality."""
from pathlib import Path
import hashlib,json,pefile
R=Path(__file__).resolve().parent.parent
m=json.loads((R/'analysis/single_exe_1412_manifest.json').read_text())
assert m['output']=='SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe'
old=(R/'analysis/single1413/SAIV_IT_Runtime.exe').read_bytes()
new=(R/'analysis/single1412_hw330/SAIV_IT_Runtime.exe').read_bytes()
p=pefile.PE(data=old);q=pefile.PE(data=new)
normalized=bytearray(new.replace(b'SIT_Import154.dll',b'SIT_Import153.dll'))
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;off=p.get_offset_from_rva(e.OffsetToData)
    normalized[off:off+e.Size]=old[off:off+e.Size]
off=p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum');normalized[off:off+4]=old[off:off+4]
assert bytes(normalized)==old
assert q.verify_checksum()
exe=R/m['output'];assert hashlib.sha256(exe.read_bytes()).hexdigest()==m['sha256']
outer=pefile.PE(str(exe))
for pe in (q,outer):
 v=pe.VS_FIXEDFILEINFO[0]
 assert (v.FileVersionMS,v.FileVersionLS,v.ProductVersionMS,v.ProductVersionLS)==(0x10004,0xc0000,0x10004,0xc0000)
expected={101:new,102:(R/'SIT_Import154.dll').read_bytes(),103:(R/'analysis/single1413/SIT_Update.exe').read_bytes()}
for k in outer.DIRECTORY_ENTRY_RESOURCE.entries:
 if k.id==10:
  for n in k.directory.entries:
   if n.id in expected:
    for l in n.directory.entries:
     e=l.data.struct;assert outer.get_data(e.OffsetToData,e.Size)==expected.pop(n.id)
assert not expected
prior=json.loads((R/'analysis/firmware1413_release_validation.json').read_text());assert prior['passed']
# Only the user-agent version string changed in the source since acceptance.
changed=[]
for line in (R/'sit_import/firmware_windows.inc').read_text().splitlines():
 if 'SAIV-IT-Firmware/' in line:changed.append(line)
assert len(changed)==1 and '/1.4.12' in changed[0]
for name in ('batch_ui.inc','conversions.inc'):
 assert (R/'sit_import'/name).read_bytes()==(R/'analysis/reference/sit_import_v1412'/name).read_bytes()
report=dict(passed=True,build=m,embedded_components_exact=True,version='1.4.12',
 native_changes_limited_to=['DLL references','About/version','PE checksum'],
 tested_functionality='analysis/firmware1413_release_validation.json',unsigned=True)
(R/'analysis/firmware1412_final_static_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
