from pathlib import Path
import subprocess,json,tempfile,math,hashlib
ROOT=Path(__file__).resolve().parent.parent;WORK=ROOT/'analysis/runtime_test';WORK.mkdir(exist_ok=True)
exe=ROOT/'analysis/parser_test_cli.exe';results=[]
def run(name,source,expected=0,oxygen=False):
 path=WORK/(name+'.txt');path.write_text(source,encoding='utf-8');p=subprocess.run([str(exe),str(path)]+(['oxygen'] if oxygen else []),capture_output=True);assert p.returncode==expected,(name,p.returncode,p.stderr.decode(errors='replace'));results.append(name);return p.stdout.decode('utf-8-sig')
def rows(text):
 ls=text.splitlines();n=next(i for i,l in enumerate(ls) if l.startswith('FIELDS:'));fields=ls[n][7:].strip().split(';');return fields,[dict(zip(fields,x.split(';'))) for x in ls[n+1:] if x.strip()]
for filename,count in [('2026_09_03_20-28-52_C.txt',79),('2026_09_07_19-34-42_C.txt',3)]:
 src=(ROOT/'data'/filename).read_text();raw=subprocess.run([str(exe),str(ROOT/'data'/filename)],capture_output=True);assert raw.returncode==0,raw.stderr;results.append(filename+'_original_bytes');out=run(filename,src);f,r=rows(out);sf,sr=rows(src);assert f==sf and r==sr and len(r)==count
 if count==79:assert r[0]['TIME']=='20:28:52' and r[1]['TIME']=='20:28:56'
 else:assert not any(x in f for x in ['T','P','C','S']);o=run('surface_oxygen',src,oxygen=True);of,rr=rows(o);assert math.isclose(float(rr[0]['OxR_mg_L']),9.02425974628226*.0029,rel_tol=1e-9);assert math.isclose(float(rr[0]['OxR_mL_L']),float(rr[0]['OxR_mg_L'])*22.391/31.998,rel_tol=1e-12)
 assert rows(run(filename+'_roundtrip',out))==(f,r)
run('APB5_legacy',(ROOT/'data/26090606_18.11.51.txt').read_text());assert run('legacy_export',(ROOT/'data/test.txt').read_text(encoding='cp1252'))=='LEGACY'
full='OSU107 Full DATE=2026-09-03 TIME=20:28:52 INTERVAL_S=2\nCTDOFOT Par OxR Ser No 1240 AP1006.175\nN00001 C42.914 T+15.000 P0000.00 OF0.38 OT1.20 Par4.26 OxR98.50 Tilt0 2026-09-03 20:28:52\nN00002 C42.914 T+15.000 P0000.01 OF0.39 OT1.21 Par4.27 OxR99.50 Tilt1 2026-09-03 20:28:56\nEnd of data\n'
f,r=rows(run('synthetic_full',full));assert r[0]['OF']=='0.38' and r[0]['OT']=='1.20' and r[0]['OxR']=='98.50' and r[1]['TIME']=='20:28:56'
f,r=rows(run('full_header_time','SAIV110 Full DATE=2026-12-31 TIME=23:59:58 INTERVAL_S=5\nN1 Par4 OxR100\nN2 Par5 OxR99\n'));assert r[1]['DATE']=='2027-01-01' and r[1]['TIME']=='00:00:03'
base='FIELDS: COUNT;Par;OxR;DATE;TIME\n1;4.25;100;2026-09-08;10:00:00\n'
run('reordered','FIELDS: DATE;OxR;COUNT;TIME;Par\n2026-09-08;100;1;10:00:00;4.25\n')
for name,s in [('bad_number',base.replace('4.25','not_a_number')),('nan',base.replace('4.25','NaN')),('infinity',base.replace('4.25','inf')),('bad_date',base.replace('2026-09-08','2026-02-30')),('bad_time',base.replace('10:00:00','25:00:00')),('missing_column',base.replace('1;4.25;100;','1;100;')),('duplicate_field',base.replace('Par;OxR','Par;Par')),('multiple_sections',base+base),('full_missing_time','SAIV110 Full\nN1 Par4 OxR100\n'),('full_unknown_text',full.replace('Par4.26','unparsed Par4.26'))]:run(name,s,2)
(WORK/'logger_parser_validation.json').write_text(json.dumps(dict(passed=len(results),cases=results),indent=2));print('PASS',len(results),'parser/roundtrip/conversion/rejection cases')
