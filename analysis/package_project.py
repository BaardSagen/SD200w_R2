"""Package the explicit transfer inventory locally; no publishing."""
from pathlib import Path
import json,zipfile,hashlib
R=Path(__file__).resolve().parent.parent;inventory=json.loads((R/'analysis/transfer_inventory.json').read_text(encoding='utf-8'));out=R/'SD200W_Prosjekt_2026-09-08.zip'
for name,expected in inventory['executable_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==expected
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for name in inventory['files']:
  p=(R/name).resolve();assert p.is_relative_to(R) and p.is_file();z.write(p,name)
with zipfile.ZipFile(out) as z:assert z.testzip() is None;count=len(z.namelist())
report=dict(archive=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,files=count,uploaded=False)
(R/'analysis/project_archive_manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
