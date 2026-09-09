from pathlib import Path
import json,math,sys
sys.path.insert(0,'analysis')
from recovered_formulas import salinity,sound_velocity,density_anomaly,gravity,oxygen_saturation_mg_l
root=Path.cwd();out=root/'analysis/runtime_test/import122';report=json.loads((out/'gui_validation.json').read_text());checks=0

def table(path):
 lines=Path(path).read_text(encoding='utf-8-sig').splitlines();i=next(i for i,l in enumerate(lines) if l.startswith('FIELDS:'));keys=lines[i][7:].strip().split(';');return lines[:i],[dict(zip(keys,l.split(';'))) for l in lines[i+1:] if l.strip()]
for case in report:
 meta,rows=table(case['export']);_,raw=table(case['file']);assert len(raw)==len(rows)==case['rows'];excluded={'C','P','Par','OX','OxR'} if case['exclude'] else set()
 for a,b in zip(raw,rows):
  for field,value in a.items():
   if field in excluded:assert field not in b
   else:assert b[field]==value,(field,b[field],value)
   checks+=1
  if 'C' in a:
   C,T,P=map(float,[a['C'],a['T'],a['P']]);S=salinity(C,T,P);g=gravity(60.3936119227684,P)
   expect={'S':S,'Depth_m':P*10000/((1000+density_anomaly(S,T,P))*g),'Sound_velocity_SIT_m_s':sound_velocity(S,T,P),'Density_anomaly_SIT_kg_m3':density_anomaly(S,T,P)}
   assert any('GPS position: 60.3936119227684, 5.29588169849683;' in m for m in meta)
  else:T,S,P=10,35,0;expect={};assert 'Depth_m' not in b and 'T' not in b and 'S' not in b
  expect['Par_umol_m2_s']=float(a['Par'])*(10000 if case['exclude'] else 1)
  for field in ['OX','OxR']:
   if field in a:
    ap=1006.175 if '09_03' in case['file'] else 1013.25
    mg=oxygen_saturation_mg_l(S,T,ap*760/1013.25)*float(a[field])/100
    expect[field+'_mg_L']=mg;expect[field+'_mL_L']=mg*22.391/31.998
  if case['exclude']:
   expect.pop('Sound_velocity_SIT_m_s',None);assert 'Sound_velocity_SIT_m_s' not in b;checks+=1
  for key,value in expect.items():assert math.isclose(float(b[key]),value,rel_tol=1e-10,abs_tol=1e-9),(case['file'],key,b[key],value);checks+=1
 if case['exclude']:assert any('multiplier=10000' in m for m in meta)
 else:assert any('multiplier=1;' in m for m in meta)
(out/'numeric_validation.json').write_text(json.dumps(dict(passed=checks,all_selected_originals_preserved=True,excluded_originals_absent=True,gps_header_validated=True),indent=2));print('PASS',checks,'values including S, real depth, GPS, both PAR unit choices and both oxygen sensors')
