from pathlib import Path
import json,zipfile,hashlib
R=Path(__file__).resolve().parent.parent;m=json.loads((R/'analysis/last_com_port_manifest.json').read_text())
assert hashlib.sha256((R/m['output']).read_bytes()).hexdigest()==m['sha256']
assert hashlib.sha256((R/m['dll']).read_bytes()).hexdigest()==m['dll_sha256']
files=[m['output'],m['dll'],'LES_MEG_Last_COM_Port_132.md']
with zipfile.ZipFile(R/'SAIV_IT_v1.3.1_portable.zip') as previous:
 files += [n for n in previous.namelist() if not n.lower().endswith(('.exe','.dll'))]
with zipfile.ZipFile(R/'SAIV_IT_v1.3.2_portable.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(R/name,name)
with zipfile.ZipFile(R/'SAIV_IT_v1.3.2_portable.zip') as z:
 assert z.testzip() is None
 for name in files:assert z.read(name)==(R/name).read_bytes()
p=R/'analysis/transfer_inventory.json';inv=json.loads(p.read_text());added=files+['SAIV_IT_v1.3.2_portable.zip','analysis/build_last_com_port.py','analysis/last_com_port.s','analysis/last_com_port_manifest.json','analysis/test_last_com_port.py','analysis/last_com_port_validation.json','analysis/check_last_com_port_windows.py','analysis/runtime_test/last_port132/gui_validation.json','analysis/package_last_com_port_132.py','analysis/last_port_disassembly.txt'];inv['files']=sorted(set(inv['files']+added));inv['executable_sha256'][m['output']]=m['sha256'];p.write_text(json.dumps(inv,indent=2),encoding='utf-8')
print('PASS portable package CRC and all',len(files),'files')
