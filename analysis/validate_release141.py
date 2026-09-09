"""Validate the built 1.4.1 release using isolated GUI/customer copies."""
import subprocess,json,pathlib,pefile,hashlib
r=pathlib.Path(__file__).resolve().parent.parent;m=json.loads((r/'analysis/single_exe_141_manifest.json').read_text())
assert hashlib.sha256((r/m['output']).read_bytes()).hexdigest()==m['sha256']
for name in [m['output'],'analysis/single141/SIT_Update.exe']:
 p=pefile.PE(str(r/name));entry=next(l.data.struct for k in p.DIRECTORY_ENTRY_RESOURCE.entries if k.id==10 for n in k.directory.entries if n.id==104 for l in n.directory.entries)
 assert p.get_data(entry.OffsetToData,entry.Size)==(r/'sit_update/miniz/LICENSE').read_bytes()
subprocess.run(['g++','-std=c++11','-O2','-static','analysis/test_update141.cpp','-o','analysis/test_protocol141.exe'],cwd=r,check=True)
subprocess.run(['g++','-std=c++11','-O2','-static','analysis/test_settings140.cpp','-o','analysis/test_settings140.exe'],cwd=r,check=True)
results=[]
for command in [['analysis/test_protocol141.exe'],['analysis/test_settings140.exe'],['python','analysis/test_settings141_hooks.py'],['python','analysis/check_update141_gui.py'],['python','analysis/check_update141_install.py'],['python','analysis/check_update141_server_install.py']]:
 p=subprocess.run(command,cwd=r,capture_output=True,text=True,timeout=150);results.append({'command':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});print(command,p.returncode,p.stdout,p.stderr,flush=True)
 (r/'analysis/runtime_test/update141/release_validation.json').write_text(json.dumps({'manifest':m,'embedded_license_verified':True,'results':results},indent=2))
 if p.returncode:raise SystemExit(p.returncode)
