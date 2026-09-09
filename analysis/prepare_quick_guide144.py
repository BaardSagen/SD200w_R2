"""Prepare the new build while keeping the 1.4.3 source and release intact."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent.parent
old=R/'analysis/reference/sit_import_v143'
assert old.is_dir() and not (old/'quick_guide.inc').exists()
build=R/'analysis/build_single_exe_143.py'
s=build.read_text()
assert "str(R/'sit_import/sit_import.cpp')" in s
new=s.replace('single143','single144').replace('Import143','Import144').replace('1.4.3','1.4.4').replace('1,4,3,0','1,4,4,0').replace('0x30000','0x40000').replace('single_exe_143','single_exe_144')
new=new.replace('single142/','single143/').replace('Import142','Import143').replace('1.4.2 Sept.2026','1.4.3 Sept.2026')
m=json.loads((R/'analysis/single_exe_143_manifest.json').read_text())
new=new.replace(m['source_sha256'],m['runtime_sha256'])
new=new.replace('Instrument settings release from preserved 1.3.8 runtime.','Quick guide release from preserved 1.4.3 runtime.')
new=new.replace('# Update-dialog hint; preserve runtime and installer from the prior release.','# Offline Quick guide; preserve instrument runtime and installer.')
needle='for name in [\'launcher.cpp\',\'launcher.manifest\']:'
new=new.replace(needle,"""# No executable code changes other than the equal-length DLL references.
patched=pefile.PE(data=bytes(b))
for section in p.sections:
 if section.Characteristics & 0x20000000:
  before=p.get_data(section.VirtualAddress,section.SizeOfRawData)
  after=patched.get_data(section.VirtualAddress,section.SizeOfRawData)
  assert after.replace(b'SIT_Import144.dll',b'SIT_Import143.dll')==before
"""+needle)
(R/'analysis/build_single_exe_144.py').write_text(new)
build.write_text(s.replace("R/'sit_import/","R/'analysis/reference/sit_import_v143/"))
p=R/'sit_import/update_ui.inc';s=p.read_text()
s=s.replace('1.4.3','1.4.4').replace('#include "update_protocol.h"','#include "update_protocol.h"\n#include "quick_guide.inc"')
needle='auto help=GetSubMenu(main,i);'
assert s.count(needle)==1
s=s.replace(needle,needle+'if(help&&GetMenuState(help,guideMenuId,MF_BYCOMMAND)==DWORD(-1)){InsertMenuW(help,0,MF_BYPOSITION|MF_STRING,guideMenuId,L"&Quick guide...");DrawMenuBar(h);}')
needle='if(m==WM_COMMAND&&LOWORD(w)==updateMenuId&&!l)'
assert s.count(needle)==1
s=s.replace(needle,'if(m==WM_COMMAND&&LOWORD(w)==guideMenuId&&!l){guideShow(h);return 0;}'+needle)
p.write_text(s)
for name in ['single_exe_test_support_143.py','native143_gui_support.py']:
 s=(R/'analysis'/name).read_text().replace('143','144')
 (R/'analysis'/name.replace('143','144')).write_text(s)
print('Prepared SIT 1.4.4; historical build 1.4.3 now uses its preserved sources.')
