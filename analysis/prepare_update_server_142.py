from pathlib import Path
import json,hashlib,zipfile
root=Path(__file__).resolve().parent.parent;folder=root/'update_server';exe=root/'SAIV_Instrument_Terminal_v1.4.2_Sept2026.exe';notes=folder/'README_v1.4.2.txt';archive=folder/(exe.stem+'.zip')
m=json.loads((root/'analysis/single_exe_142_manifest.json').read_text());assert hashlib.sha256(exe.read_bytes()).hexdigest()==m['sha256']
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 z.write(exe,exe.name);z.write(notes,'README.txt');z.write(root/'sit_update/miniz/LICENSE','THIRD_PARTY_NOTICES.txt')
public={'version':'1.4.2','url':'https://saiv.no/software/'+archive.name,'readme_url':'https://saiv.no/software/'+notes.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
(folder/'latest.json').write_text(json.dumps(public,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and z.read(exe.name)==exe.read_bytes() and z.read('README.txt')==notes.read_bytes()
print(json.dumps(public,indent=2))
