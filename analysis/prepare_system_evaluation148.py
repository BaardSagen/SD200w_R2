from pathlib import Path
import shutil
R=Path(__file__).resolve().parent.parent
archive=R/'analysis/reference/sit_import_v147'
assert not archive.exists()
shutil.copytree(R/'sit_import',archive)
for name in ['SIT_CONVERSIONS_AND_FORMULAS.md','SIT_FORMULA_REFERENCE.md']:
    shutil.copy2(R/'docs'/name,archive/name)
build=R/'analysis/build_single_exe_147.py'
original=build.read_text()
new=original.replace('147','148').replace('1.4.7','1.4.8').replace('1,4,7,0','1,4,8,0').replace('0x70000','0x80000')
(R/'analysis/build_single_exe_148.py').write_text(new)
old=original.replace("subprocess.run([sys.executable,str(R/'analysis/generate_formula_guide147.py')],check=True)", '# Guide source preserved in analysis/reference/sit_import_v147.')
old=old.replace("R/'sit_import/", "R/'analysis/reference/sit_import_v147/")
build.write_text(old)
for name in ['generate_formula_guide147.py','check_formula_guide147_gui.py','native147_gui_support.py','single_exe_test_support_147.py']:
    content=(R/'analysis'/name).read_text().replace('147','148').replace('1.4.7','1.4.8')
    (R/'analysis'/name.replace('147','148')).write_text(content)
print('Preserved 1.4.7 and prepared guide-only 1.4.8 build.')
