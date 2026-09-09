"""Create local portable/source archives; never uploads or removes prior deliveries."""
from pathlib import Path
import zipfile,hashlib,json,subprocess
S=Path(__file__).resolve().parent;out=S/'releases';out.mkdir(exist_ok=True)
subprocess.run(['cmake','--install',str(S/'build'),'--prefix',str(S/'dist/SAIVStudio-0.2.0')],check=True)
packages={}
for name,root,files in [
 ('SAIVStudio_0.2.0_Windows_x64.zip',S/'dist/SAIVStudio-0.2.0',None),
 ('SAIVStudio_0.2.0_Source.zip',S,sorted(p for base in ['src','assets','tests','samples','docs','vendor','test-results'] for p in (S/base).rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts)+[S/x for x in ['CMakeLists.txt','build.cmd','package.py','README.md','THIRD_PARTY_NOTICES.md']])]:
 files=files or sorted(p for p in root.rglob('*') if p.is_file())
 with zipfile.ZipFile(out/name,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,p.relative_to(root).as_posix())
 with zipfile.ZipFile(out/name) as z:assert z.testzip() is None
 packages[name]={'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'bytes':(out/name).stat().st_size,'files':len(files)}
(out/'manifest_0.2.0.json').write_text(json.dumps(packages,indent=2));print(json.dumps(packages,indent=2))
