from pathlib import Path
import shutil
R=Path(__file__).resolve().parent.parent
A=R/'analysis/reference/sit_import_v148'
assert not A.exists()
shutil.copytree(R/'sit_import',A)
for n in ['SIT_CONVERSIONS_AND_FORMULAS.md','SIT_FORMULA_REFERENCE.md']:
    shutil.copy2(R/'docs'/n,A/n)
p=R/'analysis/build_single_exe_148.py';old=p.read_text()
new=old
for a,b in [('single148','single149'),('Import148','Import149'),('guide148','guide149'),('exe_148','exe_149'),('1.4.8','1.4.9'),('1,4,8,0','1,4,9,0'),('0x80000','0x90000')]:new=new.replace(a,b)
(R/'analysis/build_single_exe_149.py').write_text(new)
old=old.replace("subprocess.run([sys.executable,str(R/'analysis/generate_formula_guide148.py')],check=True)", '# Guide source preserved in analysis/reference/sit_import_v148.')
p.write_text(old.replace("R/'sit_import/","R/'analysis/reference/sit_import_v148/"))
for n in ['check_formula_guide148_gui.py','native148_gui_support.py','single_exe_test_support_148.py']:
    s=(R/'analysis'/n).read_text().replace('148','149').replace('1.4.8','1.4.9')
    (R/'analysis'/n.replace('148','149')).write_text(s)
p=R/'sit_import/update_ui.inc';p.write_text(p.read_text().replace('"1.4.8"','"1.4.9"'))
p=R/'sit_import/quick_guide.inc';s=p.read_text()
s=s.replace('Start with System evaluation for a plain-language recommendation. System: measurement quality explains the reasons; parameter topics contain the formulas.', 'Start with System evaluation for a short recommendation. Select a measurement topic for its method and an example.')
p.write_text(s)
# Correct a reference-comment typo caused by the old guide generator's broad
# version replacement. The actual sound-speed calculation was unaffected.
p=R/'docs/SIT_FORMULA_REFERENCE.md';p.write_text(p.read_text(encoding='utf-8').replace('1488.82737409','1478.82737409'),encoding='utf-8')
print('Preserved 1.4.8; prepared 1.4.9.')
