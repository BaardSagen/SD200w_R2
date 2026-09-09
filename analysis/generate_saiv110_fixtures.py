"""Generate clearly marked synthetic logger fixtures. Never edit source measurements."""
from pathlib import Path
from datetime import datetime,timedelta
import json
root=Path(__file__).resolve().parent.parent
p=root/'data/saiv110';p.mkdir(exist_ok=True)
base=root/'data/2026_09_07_19-34-42_C.txt';assert base.exists()
start=datetime(2026,9,3,20,28,52)
cases=[('01_exact_long_before.txt',-300,5,130),('02_starts_late.csv',60,3,100),('03_short_exact.txt',30,2,4),('04_offset_0p5s.csv',0.5,2,50),('05_offset_5s_short.txt',-5,1,1),('06_offset_10s_boundary.txt',-10,1,1),('07_outside_10s.txt',-10.1,1,1),('08_wrong_date.txt',86400,5,100),('09_ends_before.txt',-600,5,80),('10_starts_after.txt',600,5,80),('11_few_late_rows.csv',155,2.5,5),('12_many_fast_rows.csv',-120,0.5,1000)]
manifest=[]
for name,offset,step,count in cases:
 first=start+timedelta(seconds=offset)
 lines=['# SYNTHETIC TEST DATA - NOT REAL MEASUREMENTS',f'# Based on {base.name}; generated for OSU107 timestamp matching',f'SAIV110(S-L) Ser:107 DATE={first:%Y-%m-%d} TIME={first:%H:%M:%S} (LT) INTERVAL_S={step} TOTAL_COUNTER={count}','FIELDS: COUNT;Par;OxR;Tilt;DATE;TIME']
 for i in range(count):
  t=first+timedelta(seconds=i*step)
  tm=t.strftime('%H:%M:%S')+(('.%06d'%t.microsecond).rstrip('0') if t.microsecond else '')
  lines.append(f'{i+1};{4.25+(i%9)*.01:.2f};{.29+(i%4)*.01:.2f};{i%3};{t:%Y-%m-%d};{tm}')
 (p/name).write_text('\n'.join(lines)+'\n',encoding='utf-8')
 manifest.append(dict(file=name,start=first.isoformat(),rows=count,interval_seconds=step,offset_from_osu_start_seconds=offset))
(p/'fixtures.json').write_text(json.dumps(manifest,indent=2))
(p/'LES_MEG.md').write_text('''# Syntetiske SAIV110-testfiler

Alle filer er merket SYNTHETIC TEST DATA. Sensorverdiene er kunstige og bygger på formatet i 2026_09_07_19-34-42_C.txt. Originalfilene er urørt.

Master: ../2026_09_03_20-28-52_C.txt (OSU107, 79 rader, 20:28:52–20:31:30 den 3. september 2026).

01 starter fem minutter før og fortsetter etter master. 02 starter ett minutt etter. 03 har fire eksakte treff. 04 har halvt sekund avvik. 05 og 06 ligger henholdsvis 5 og 10 sekunder før første masterrad. 07 ligger 10,1 sekunder før og skal aldri matche ved tillatt toleranse. 08 har feil dato. 09 slutter lenge før. 10 starter lenge etter. 11 har noen få rader mot slutten. 12 har 1000 rader med 0,5 sekund intervall og starter to minutter før.

fixtures.json inneholder start, intervall og radantall. Regenerer med analysis/generate_saiv110_fixtures.py.
''',encoding='utf-8')
print('Generated',len(cases),'synthetic fixtures')
