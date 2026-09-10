"""Collect finished release evidence; refuse stale GUI results."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parent.parent
read=lambda p:json.loads((R/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
m=read('analysis/single_exe_147_manifest.json')
assert sha(m['output'])==m['sha256']
assert sha('SIT_Import147.dll')==m['dll_sha256']
gui=read('analysis/runtime_test/models147gui/gui_validation.json')
guide=read('analysis/runtime_test/guide147/gui_validation.json')
numeric=read('analysis/models147/validation.json')
assert gui['shipped_exe_sha256']==guide['shipped_exe_sha256']==m['sha256']
assert gui['native_import_and_reopen_preserve_model_columns']
assert gui['preset_models_retained'] and gui['legacy_43_rows'] and gui['surface_support_back_and_atlas']
assert len(guide['topics'])==31 and guide['full_formula_text_matches_source']
assert 'PASS 409 ' in numeric['result']
source=(R/'docs/SIT_CONVERSIONS_AND_FORMULAS.md').read_text(encoding='utf-8')
assert not re.search(r'26090606|Lungeg|APB5|Bergen',source,re.I)
conductivity=source.split('## Conductivity and salinity\n')[1].split('\n## ')[0]
assert conductivity.strip().split('\n\n')[-1].startswith('SAIV recommends recording in CTD mode')
vendor=read('sit_import/vendor/gsw/SIT_SOURCE_MANIFEST.json')
for name,digest in vendor['sha256'].items():assert sha('sit_import/vendor/gsw/'+name)==digest
native=read('analysis/formula_guide146_validation.json')
report={}
report.update(release=m,numeric=numeric,native_equation_checks=len(native['checks']),guide_topics=len(guide['topics']),
 gui=gui,guide=guide,guide_example_provenance_omitted=True,SAIV_recommendation_last_in_conductivity=True,
 instrument_commands_sent=False,physical_calibration_validation=False,published_or_pushed=False)
(R/'analysis/models147_release_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS final release',m['output'],m['sha256'],'409 numerical/integration checks; 31 guide topics; GUI and SD2 reopened')
