import json,math,sys
from pathlib import Path
sys.path.insert(0,'analysis')
from recovered_formulas import salinity,sound_velocity,density_anomaly,oxygen_saturation_mg_l
report=json.loads(Path('analysis/runtime_test/logger_import_gui_validation.json').read_text());checks=0
for case in report:
 if 'export' not in case:continue
 def table(s):
  ls=s.splitlines();i=next(i for i,l in enumerate(ls) if l.startswith('FIELDS:'));f=ls[i][7:].strip().split(';');return [dict(zip(f,l.split(';'))) for l in ls[i+1:] if l.strip()]
 original=table((Path('data')/case['file']).read_text());exported=table(Path(case['export']).read_text(encoding='utf-8-sig'))
 for a,b in zip(original,exported):
  assert all(b[k]==v for k,v in a.items());checks+=1
  if 'C' in a:
   t=float(a['T']);p=float(a['P']);s=salinity(float(a['C']),t,p);ap=1006.175
   for k,v in [('Salinity_SIT',s),('Sound_velocity_SIT_m_s',sound_velocity(s,t,p)),('Density_anomaly_SIT_kg_m3',density_anomaly(s,t,p))]:assert math.isclose(float(b[k]),v,rel_tol=1e-10,abs_tol=1e-9),(k,b[k],v);checks+=1
  else:t,s,ap=10,35,1013.25
  mg=oxygen_saturation_mg_l(s,t,ap*760/1013.25)*float(a['OxR'])/100
  assert math.isclose(float(b['OxR_mg_L']),mg,rel_tol=1e-10);assert math.isclose(float(b['OxR_mL_L']),mg*22.391/31.998,rel_tol=1e-10);checks+=2
Path('analysis/runtime_test/logger_export_numeric_validation.json').write_text(json.dumps(dict(checks=checks,all_original_fields_and_timestamps_unchanged=True),indent=2));print('PASS',checks,'exported value checks')
