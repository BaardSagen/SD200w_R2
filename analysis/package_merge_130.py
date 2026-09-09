"""Package verified binaries and synthetic fixtures, then update transfer inventory."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parent.parent
m=json.loads((ROOT/'analysis/logger_import_130_manifest.json').read_text())
files=[m['output'],'SIT_Import130.dll','LES_MEG_Merge_130.md','LES_MEG_Import_122.md','LES_MEG_Import_121.md','data/2026_09_03_20-28-52_C.txt','data/2026_09_07_19-34-42_C.txt']+[p.relative_to(ROOT).as_posix() for p in (ROOT/'data/saiv110').iterdir() if p.is_file()]
assert hashlib.sha256((ROOT/m['output']).read_bytes()).hexdigest()==m['sha256']
assert hashlib.sha256((ROOT/'SIT_Import130.dll').read_bytes()).hexdigest()==m['dll_sha256']
package=ROOT/'SAIV_IT_v1.3.0_portable.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(ROOT/f,f)
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None
 for f in files:assert z.read(f)==(ROOT/f).read_bytes()
added=files+['SAIV_IT_v1.3.0_portable.zip','analysis/package_merge_130.py','analysis/check_merge_portable.py','analysis/build_logger_import_130.py','analysis/logger_import_130_manifest.json','analysis/generate_saiv110_fixtures.py','analysis/merge_test_cli.cpp','analysis/check_merge_values.py','analysis/check_merge_windows.py','analysis/check_merge_extra_windows.py','analysis/check_merge_gui_values.py','analysis/check_merge_hook.py','analysis/capture_merge_window.py','analysis/check_logger_import_130_windows.py','analysis/check_logger_import_130_values.py','analysis/check_logger_hook_130.py','sit_import/merge.h','sit_import/merge_ui.inc','sit_import/import_hook_130.s','analysis/runtime_test/logger_hook_130_validation.json','analysis/runtime_test/merge130/merge_printwindow.png']
added += [p.relative_to(ROOT).as_posix() for p in (ROOT/'analysis/reference/sit_import_v122').iterdir() if p.is_file()]
for folder in ['merge130','import130']:
 added += [p.relative_to(ROOT).as_posix() for p in (ROOT/'analysis/runtime_test'/folder).glob('*validation.json')]
p=ROOT/'analysis/transfer_inventory.json';inv=json.loads(p.read_text());inv['files']=sorted(set(inv['files']+added));inv['executable_sha256'][m['output']]=m['sha256'];inv['executable_sha256']['SIT_Import130.dll']=m['dll_sha256'];p.write_text(json.dumps(inv,indent=2),encoding='utf-8')
print('PASS package CRC/content:',len(files),'files,',package.stat().st_size,'bytes')
