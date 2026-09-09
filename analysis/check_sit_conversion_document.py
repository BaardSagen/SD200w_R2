"""Verify the reference code embedded in the revised document against recorded EXE calls."""
from pathlib import Path
import re,json,math,hashlib
ROOT=Path(__file__).resolve().parent.parent
path=ROOT/'docs/konverteringer_og_eksport.md';text=path.read_text(encoding='utf-8')
blocks=re.findall(r'```python\n(.*?)\n```',text,re.S);assert len(blocks)==1
scope={};exec(compile(blocks[0],str(path),'exec'),scope)
checks=[]
def check(label,actual,expected):
 assert math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-8),(label,actual,expected)
 checks.append(dict(test=label,document=actual,exe_reference=expected))
for row in json.loads((ROOT/'analysis/formula_numeric_validation.json').read_text()):
 name=row['formula'];args=row['args']
 if name in ('sound_velocity','density_anomaly','legacy_sigma'):
  P,T,S=args;value=scope['legacy_sigma'](S,T) if name=='legacy_sigma' else scope[name](S,T,P)
 elif name=='sigma_t':T,S=args;value=scope['density0'](S,T)-1000
 elif name=='salinity':C,T,P=args;value=scope['salinity'](C,T,P)
 else:raise AssertionError(name)
 check(name+str(args),value,row['binary'])
for row in json.loads((ROOT/'analysis/conversion_document_comparison.json').read_text())['comparisons']:
 x=row['input'];q=row['quantity']
 if q=='salinity':value=scope['salinity'](x['C'],x['T'],x['P'])
 elif q=='sound_m_s':value=scope['sound_velocity'](x['S'],x['T'],x['P'])
 else:value=scope['oxygen_from_percent'](100,x['S'],x['T'],x['air_mmHg'])
 check('SIT 1.1.3 '+q+str(x),value,row['exe'])
assert '35.00000000000' not in text.split('## 10.')[1].split('## 11.')[0]
assert 'C < 0.01' in text and '22.391 / 31.998' in text
report=dict(result='PASS',count=len(checks),document_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),checks=checks,scope='Embedded formulas versus 31 recorded machine-code results; not full export UI or other-program verification')
(ROOT/'analysis/sit_conversion_document_validation.json').write_text(json.dumps(report,indent=2))
print('PASS',len(checks),'document formula checks against recorded EXE results')
