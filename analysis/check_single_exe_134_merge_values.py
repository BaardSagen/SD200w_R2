"""Check the actual GUI exports against independent nearest timestamp selection."""
from pathlib import Path
from datetime import datetime,timedelta
import csv,json
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'analysis/runtime_test/single134'
report=json.loads((OUT/'gui_validation.json').read_text())
def table(path):
 lines=path.read_text(encoding='utf-8-sig').splitlines();h=next(i for i,l in enumerate(lines) if l.startswith('FIELDS:'))
 fields=next(csv.reader([lines[h][7:].strip()],delimiter=';'))
 return [dict(zip(fields,r)) for r in csv.reader(lines[h+1:],delimiter=';') if r and not r[0].startswith('#')]
def dt(r):return datetime.fromisoformat(r['DATE']+'T'+r['TIME'])
master=table(ROOT/'data/2026_09_03_20-28-52_C.txt');sources=[table(ROOT/'data/saiv110/01_exact_long_before.txt'),table(ROOT/'data/saiv110/02_starts_late.csv')]
checks=0
for separator in [False,True]:
 rows=table(Path(report['export_separator_'+str(separator)]));assert len(rows)==len(master)==79
 for row,m in zip(rows,master):
  for k,v in m.items():assert row[k]==v;checks+=1
  for idx,source in enumerate(sources,1):
   prefix=f'M{idx}_';near=min(enumerate(source),key=lambda p:(abs(dt(p[1])-dt(m)),dt(p[1]),p[0]))[1]
   delta=(dt(near)-dt(m)).total_seconds();hit=abs(delta)<=.5
   for k,v in near.items():assert row[prefix+k]==(v if hit else '');checks+=1
   assert row[prefix+'Delta_seconds']==(str(int(delta)) if hit else '');checks+=1
   if separator:assert row[prefix+'separator']=='-'
   else:assert prefix+'separator' not in row
   checks+=1
(OUT/'gui_numeric_validation.json').write_text(json.dumps(dict(checks=checks,master_rows=79,additional_files=2,both_separator_modes=True),indent=2))
print('PASS',checks,'values in actual GUI exports')
