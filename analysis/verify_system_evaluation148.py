"""Check the new assessment's examples and preserve conversion implementation."""
from pathlib import Path
import runpy, json, math
R=Path(__file__).resolve().parent.parent
fw=runpy.run_path(str(R/'asmCTDdoc/sd208-calculations-reference.py'))
native=runpy.run_path(str(R/'analysis/recovered_formulas.py'))
examples=[]
for c,t,p in [(42.914,15,0),(40,10,1000),(30,10,100),(0,15,0)]:
    a=fw['salinity'](c,t,p);b=native['salinity'](c,t,p)
    assert abs(a-b)<0.00001
    examples.append(dict(C=c,T=t,P=p,firmware_SP=a,native_SP=b,difference=a-b))
assert round(examples[0]['firmware_SP'],7)==34.9999986
assert round(examples[0]['native_SP'],7)==34.9999999
sound_checks=0
for s in [0,2,20,35,40]:
    for t in [0,10,30]:
        for p in [0,100,1000,6000]:
            assert math.isclose(fw['sound_velocity'](s,t,p),native['sound_velocity'](s,t,p),abs_tol=1e-8)
            sound_checks+=1
assert math.isclose(280.923-273.15,7.773,abs_tol=1e-10)
assert math.isclose(280.923-273.16,7.763,abs_tol=1e-10)
assert math.isclose(10*1.00024-10,.0024,abs_tol=1e-10)
assert round(35*35.16504/35,5)==35.16504
archive=R/'analysis/reference/sit_import_v147'
changed=[]
for old in archive.rglob('*'):
    if old.is_file() and old.suffix!='.md':
        relative=old.relative_to(archive)
        current=R/'sit_import'/relative
        assert current.exists(),str(relative)
        if current.read_bytes()!=old.read_bytes():changed.append(relative.as_posix())
assert set(changed)=={'formula_guide.inc','quick_guide.inc','update_ui.inc'},changed
guide=(R/'docs/SIT_CONVERSIONS_AND_FORMULAS.md').read_text(encoding='utf-8')
for forbidden in ['26090606','lungeg','apb5','bergen']:
    assert forbidden not in guide.lower(),forbidden
main=guide.split('## System evaluation\n')[1].split('\n## ')[0]
assert len(main.split())<600,len(main.split())
report=dict(examples=examples,sound_comparisons=sound_checks,changed_import_files=changed,
            summary_words=len(main.split()),privacy_check=True,calculation_sources_unchanged=True)
(R/'analysis/system_evaluation148_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
