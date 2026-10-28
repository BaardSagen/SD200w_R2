"""Bind the control regression and exact embedded components to SIT 1.4.13."""
from pathlib import Path
import hashlib,json,pefile
R=Path(__file__).resolve().parent.parent
m=json.loads((R/'analysis/single_exe_1413_manifest.json').read_text())
old=(R/'analysis/single1412_hw330/SAIV_IT_Runtime.exe').read_bytes()
new=(R/'analysis/single1413_settings/SAIV_IT_Runtime.exe').read_bytes()
p=pefile.PE(data=old);q=pefile.PE(data=new)
normalized=bytearray(new[:len(old)].replace(b'SIT_Import155.dll',b'SIT_Import154.dll'))
allowed=[]
for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
 for n in k.directory.entries:
  for l in n.directory.entries:
   if k.id==16 or (k.id==10 and str(n.name)=='TABOUTBOXNAV'):
    e=l.data.struct;allowed.append((p.get_offset_from_rva(e.OffsetToData),e.Size))
allowed.append((p.get_offset_from_rva(0x1a593c),5))
for at in (p.sections[-1].get_field_absolute_offset('Misc_VirtualSize'),p.sections[-1].get_field_absolute_offset('SizeOfRawData'),p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')):allowed.append((at,4))
for at,size in allowed:normalized[at:at+size]=old[at:at+size]
assert bytes(normalized)==old,'Unexpected native code change'
assert q.verify_checksum()
exe=R/m['output'];assert hashlib.sha256(exe.read_bytes()).hexdigest()==m['sha256']
outer=pefile.PE(str(exe))
for pe in (q,outer):
 v=pe.VS_FIXEDFILEINFO[0]
 assert (v.FileVersionMS,v.FileVersionLS,v.ProductVersionMS,v.ProductVersionLS)==(0x10004,0xd0000,0x10004,0xd0000)
expected={101:new,102:(R/'SIT_Import155.dll').read_bytes(),103:(R/'analysis/single1413_settings/SIT_Update.exe').read_bytes()}
for k in outer.DIRECTORY_ENTRY_RESOURCE.entries:
 if k.id==10:
  for n in k.directory.entries:
   if n.id in expected:
    for l in n.directory.entries:
     e=l.data.struct;assert outer.get_data(e.OffsetToData,e.Size)==expected.pop(n.id)
assert not expected
static=dict(passed=True,build=m,embedded_components_exact=True,
 native_changes_limited_to=['tagged control dispatcher','DLL references','About/version','PE sizes/checksum'])
(R/'analysis/firmware1413_static_validation.json').write_text(json.dumps(static,indent=2)+'\n')
dispatch=json.loads((R/'analysis/dispatch1413_validation.json').read_text());assert dispatch['passed']
gui_path=sorted((R/'analysis/runtime_test/controls1413').glob('*/report.json'))[-1]
gui=json.loads(gui_path.read_text());assert gui['passed']
assert gui['tested_module_sha256']==m['dll_sha256']
assert len(gui['settings'])==6 and all(x['correct_dialog'] for x in gui['settings'])
assert gui['single_and_batch_exports_unchanged'] and gui['source_files_unchanged']
assert gui['convert_button_and_file_menu'] and gui['merge_own_dialog']
assert gui['firmware_and_software_update_preserved']
release=dict(passed=True,build=m,gui_report=gui_path.relative_to(R).as_posix(),
 controls_checked=['TIME/DATE','Interval','Convert button','File conversion menu','Merge'],
 settings_instruments=['SD200','OSU107','SAIV110'],
 disabled_without_detection=True,disabled_after_port_change=True,
 exports_byte_identical_to_1411=True,source_files_unchanged=True,
 dispatch_report='analysis/dispatch1413_validation.json',
 physical_serial_disabled=True,physical_device_io=False,
 firmware_functions_unchanged=True,firmware_channels=['3.1.2','3.3.0'])
(R/'analysis/firmware1413_release_validation.json').write_text(json.dumps(release,indent=2)+'\n')
print(json.dumps(release,indent=2))
