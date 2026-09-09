"""Independent nearest-time oracle, fixture coverage and lossless merge checks."""
from pathlib import Path
from datetime import datetime,timedelta
import subprocess,csv,io,json,random,hashlib
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'analysis/runtime_test/merge130';OUT.mkdir(exist_ok=True)
CLI=ROOT/'analysis/merge_test_cli.exe'
checks=0
def table(path):
 lines=path.read_text(encoding='utf-8-sig').splitlines()
 h=next(i for i,l in enumerate(lines) if l.startswith('FIELDS:') or l.startswith('DATE;') or l.startswith('"DATE",'))
 sep=',' if lines[h].startswith('"DATE",') else ';'
 keys=next(csv.reader([lines[h].removeprefix('FIELDS:').strip()],delimiter=sep))
 return [dict(zip(keys,row)) for row in csv.reader(lines[h+1:],delimiter=sep) if row and not row[0].startswith('#')]
def dt(row):return datetime.fromisoformat(row['DATE']+'T'+row['TIME'])
def run(a,b,tol,out=None,sep=False,third=None):
 args=[str(CLI),str(a),str(b),str(tol)]
 if out:args += [str(out),'1' if sep else '0']
 if third:args += [str(third)]
 return subprocess.run(args,capture_output=True,text=True)
def compare(a,b,tol):
 global checks
 aa,bb=table(a),table(b);r=run(a,b,tol);assert r.returncode==0,r.stderr
 count,maxdelta=map(int,r.stdout.splitlines()[0].split());actual=list(map(int,r.stdout.splitlines()[1].split()))
 expected=[];deltas=[]
 for row in aa:
  t=dt(row);best=min(range(len(bb)),key=lambda i:(abs(dt(bb[i])-t),dt(bb[i]),i))
  diff=abs(dt(bb[best])-t);us=diff//timedelta(microseconds=1)
  if us<=round(tol*1e6):expected.append(best);deltas.append(us)
  else:expected.append(-1)
 assert actual==expected,(a,b,tol,actual,expected)
 assert count==len(deltas) and maxdelta==max(deltas,default=0)
 checks+=len(aa)+2
 return count
master=ROOT/'data/2026_09_03_20-28-52_C.txt'
fixtures=sorted((ROOT/'data/saiv110').glob('*.txt'))+sorted((ROOT/'data/saiv110').glob('*.csv'))
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in fixtures+[master]}
coverage=[]
for f in fixtures:
 for tol in [0,.1,.5,1,5,10]:coverage.append(dict(file=f.name,tolerance=tol,matches=compare(master,f,tol)))
for name in ['07_outside_10s.txt','08_wrong_date.txt','09_ends_before.txt','10_starts_after.txt']:
 assert all(r['matches']==0 for r in coverage if r['file']==name)
assert next(r['matches'] for r in coverage if r['file']=='06_offset_10s_boundary.txt' and r['tolerance']==10)==1
assert next(r['matches'] for r in coverage if r['file']=='04_offset_0p5s.csv' and r['tolerance']==0)==0
random.seed(107110)
def synthetic(path,stamps,comma=False):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f,delimiter=',' if comma else ';',quoting=csv.QUOTE_ALL if comma else csv.QUOTE_MINIMAL)
  w.writerow(['DATE','TIME','Value','Note'])
  for i,t in enumerate(stamps):w.writerow([t.strftime('%Y-%m-%d'),t.strftime('%H:%M:%S.%f'),str(-i-.25),'test; "quoted" value'])
a=OUT/'random_master.csv';b=OUT/'random_other.csv';origin=datetime(2026,12,31,23,59,50)
synthetic(a,[origin+timedelta(microseconds=random.randrange(-30_000_000,30_000_001)) for _ in range(200)],True)
synthetic(b,[origin+timedelta(microseconds=random.randrange(-30_000_000,30_000_001)) for _ in range(250)],True)
for tol in [0,.000001,.1,.5,1,3.4,10]:compare(a,b,tol)
# Ties and duplicate timestamps, unsorted source, and crossing midnight.
synthetic(a,[origin+timedelta(seconds=x) for x in [0,1,2,10]])
synthetic(b,[origin+timedelta(seconds=x) for x in [2,0,0,11,9]])
compare(a,b,1)
for sep in [False,True]:
 target=OUT/('merged_separator.txt' if sep else 'merged_standard.txt')
 first=ROOT/'data/saiv110/03_short_exact.txt';second=ROOT/'data/saiv110/02_starts_late.csv'
 r=run(master,first,0,target,sep,second);assert r.returncode==0,r.stderr
 rows,raw=table(target),table(master);assert len(rows)==len(raw)==79
 for row,original in zip(rows,raw):
  for k,v in original.items():assert row[k]==v;checks+=1
  for prefix,src in [('M1_',first),('M2_',second)]:
   candidates=[x for x in table(src) if dt(x)==dt(original)]
   if sep:assert row[prefix+'separator']=='-';checks+=1
   else:assert prefix+'separator' not in row;checks+=1
   if candidates:
    for k,v in candidates[0].items():assert row[prefix+k]==v;checks+=1
    assert row[prefix+'Delta_seconds']=='0'
   else:assert all(row[prefix+k]=='' for k in table(src)[0]);checks+=1
 # Merge output can be read again, including '-' and blank unmatched cells.
 r=run(target,first,0);assert r.returncode==0,r.stderr
target=OUT/'quoted_output.txt';r=run(a,b,1,target,True);assert r.returncode==0,r.stderr
assert all(row['Note']=='test; "quoted" value' for row in table(target))
assert run(target,b,1).returncode==0
for tol in ['-0.1','10.1','nan','inf','bad']:
 assert run(master,fixtures[0],tol).returncode==1;checks+=1
assert run(master,fixtures[0],'0,5').returncode==0
bad=OUT/'bad.txt';bad.write_text('DATE;TIME;X\n2026-02-30;12:00:00;1\n');assert run(bad,fixtures[0],0).returncode==1
bad.write_text('DATE;TIME;X\n2026-09-03;25:00:00;1\n');assert run(bad,fixtures[0],0).returncode==1
assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==v for f,v in hashes.items())
(OUT/'numeric_validation.json').write_text(json.dumps(dict(checks=checks,fixture_cases=coverage,source_files_unchanged=True,random_seed=107110),indent=2))
print('PASS',checks,'independent timestamp/value checks; boundaries, dates, duplicates, ties, two files, separators, CSV quoting, unmatched rows, input preservation')
