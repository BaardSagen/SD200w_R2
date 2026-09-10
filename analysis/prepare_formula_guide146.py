"""Preserve 1.4.5 sources and prepare a documentation-only 1.4.6 build."""
from pathlib import Path
import json, shutil
R=Path(__file__).resolve().parent.parent
archive=R/'analysis/reference/sit_import_v145'
assert not archive.exists(), 'Run preparation only once'
shutil.copytree(R/'sit_import',archive)
p=R/'analysis/build_single_exe_145.py';s=p.read_text()
p.write_text(s.replace("R/'sit_import/","R/'analysis/reference/sit_import_v145/"))
new=s.replace('single145','single146').replace('Import145','Import146').replace('1.4.5','1.4.6').replace('1,4,5,0','1,4,6,0').replace('0x50000','0x60000').replace('single_exe_145','single_exe_146')
new=new.replace('single144/','single145/').replace('Import144','Import145').replace('1.4.4 Sept.2026','1.4.5 Sept.2026')
m=json.loads((R/'analysis/single_exe_145_manifest.json').read_text())
new=new.replace(m['source_sha256'],m['runtime_sha256'])
new=new.replace('from patch_about_icon145 import patch_about_icon\nb=patch_about_icon(b)\n','')
new=new.replace('About instrument icon release from preserved 1.4.4 runtime.','Conversions and formulas guide from preserved 1.4.5 runtime.')
(R/'analysis/build_single_exe_146.py').write_text(new)
p=R/'sit_import/update_ui.inc';p.write_text(p.read_text().replace('"1.4.5"','"1.4.6"'))
for name in ['single_exe_test_support_145.py','native145_gui_support.py']:
 (R/'analysis'/name.replace('145','146')).write_text((R/'analysis'/name).read_text().replace('145','146'))
print('Preserved 1.4.5; prepared 1.4.6')
