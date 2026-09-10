"""Preserve the completed 1.4.6 guide-only build before conversion changes."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parent.parent
archive=R/'analysis/reference/sit_import_v146'
assert not archive.exists();shutil.copytree(R/'sit_import',archive)
p=R/'analysis/build_single_exe_146.py';s=p.read_text()
s=s.replace("subprocess.run([sys.executable,str(R/'analysis/generate_formula_guide146.py')],check=True)\n",'')
p.write_text(s.replace("R/'sit_import/","R/'analysis/reference/sit_import_v146/"))
for name in ['SIT_CONVERSIONS_AND_FORMULAS.md','SIT_FORMULA_REFERENCE.md']:
 shutil.copyfile(R/'docs'/name,archive/name)
new=s.replace('single146','single147').replace('Import146','Import147').replace('1.4.6','1.4.7').replace('1,4,6,0','1,4,7,0').replace('0x60000','0x70000').replace('single_exe_146','single_exe_147')
new=new.replace('single145/','single146/').replace('Import145','Import146').replace('1.4.5 Sept.2026','1.4.6 Sept.2026')
m=json.loads((R/'analysis/single_exe_146_manifest.json').read_text());new=new.replace(m['source_sha256'],m['runtime_sha256'])
(R/'analysis/build_single_exe_147.py').write_text(new)
p=R/'sit_import/update_ui.inc';p.write_text(p.read_text().replace('"1.4.6"','"1.4.7"'))
vendor=R/'sit_import/vendor/gsw';vendor.mkdir(parents=True)
names=['LICENSE','README','gswteos-10.h','gsw_internal_const.h','gsw_saar_data.h','gsw_saar.c','gsw_oceanographic_toolbox.c']
for name in names:shutil.copyfile(R/'saiv-studio/vendor/gsw'/name,vendor/name)
for name in ['single_exe_test_support_146.py','native146_gui_support.py']:
 (R/'analysis'/name.replace('146','147')).write_text((R/'analysis'/name).read_text().replace('146','147'))
print('Preserved guide-only 1.4.6 and vendored unchanged GSW source for SIT')
