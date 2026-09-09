from pathlib import Path
import json,hashlib,zipfile
r=Path(__file__).resolve().parents[1]
p=r/'saiv-studio/tests/terminal_input_windows.py'
p.write_text('''"""Run the current Studio GUI test from the complete project checkout."""
from pathlib import Path
import runpy
script=Path(__file__).resolve().parents[2]/'analysis/test_studio_gui030.py'
if not script.is_file():
    raise SystemExit('GUI verification requires the complete project checkout, including analysis/. Core tests run with build.cmd.')
runpy.run_path(str(script),run_name='__main__')
''',encoding='utf-8')
method='Owned test window; pointer events use the ImGui input queue after backend refresh, enabled only by --terminal-test. WM_CHAR follows the normal foreground/popup guards. File-backed transport; no instrument port, disk update or printer output.'
p=r/'analysis/test_studio_gui030.py';s=p.read_text();s=s.replace('Owned HWND messages; real GUI and file-backed terminal transport. No physical instrument, disk update or printer output.',method);p.write_text(s)
p=r/'saiv-studio/test-results/v030/gui_validation.json';gui=json.loads(p.read_text());gui['method']=method;p.write_text(json.dumps(gui,indent=2))
p=r/'analysis/studio030_release_validation.json';report=json.loads(p.read_text());report['gui']=gui
exe=r/report['exe'];assert hashlib.sha256(exe.read_bytes()).hexdigest()==report['sha256']==gui['exe_sha256']
with zipfile.ZipFile(r/report['archive']) as z:
 assert z.testzip() is None
 assert hashlib.sha256(z.read('SAIVStudio-0.3.0/SAIVStudio.exe')).hexdigest()==report['sha256']
report['zip_crc_and_executable_hash']='PASS';report['visual_review']=['terminal','setup','time_graphs','profiles','multigraph','minimum_terminal','convert_1','converted_table','merge','legacy_sd2','csv_reopened']
p.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: delivered EXE equals GUI-tested build; ZIP CRC and embedded executable hash verified.')
