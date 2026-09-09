"""Read-only inventory of the supplied import fixtures; no conversion or instrument IO."""
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import hashlib,json,re,struct
ROOT=Path(__file__).resolve().parent.parent
reports=[]
for path in sorted((ROOT/'data').glob('*.txt')):
 raw=path.read_bytes()
 try:text=raw.decode('utf-8-sig');encoding='utf-8'
 except UnicodeDecodeError:text=raw.decode('cp1252');encoding='cp1252'
 lines=text.splitlines();entry=dict(file=path.name,sha256=hashlib.sha256(raw).hexdigest(),encoding=encoding)
 fields=next((i for i,line in enumerate(lines) if line.startswith('FIELDS:')),None)
 if fields is not None:
  columns=[x.strip() for x in lines[fields].split(':',1)[1].split(';')];rows=[];timestamps=[]
  for number,line in enumerate(lines[fields+1:],fields+2):
   if not line.strip():continue
   values=line.split(';');assert len(values)==len(columns),(path.name,number)
   row=dict(zip(columns,values));timestamps.append(datetime.fromisoformat(row['DATE']+'T'+row['TIME']))
   for key,value in row.items():
    if key not in ('DATE','TIME'):assert Decimal(value).is_finite(),(path.name,number,key)
   rows.append(row)
  entry.update(format='logger_fields',logger='OSU107' if lines[0].startswith('OSU107') else 'SAIV110 SurfaceLogger',metadata=lines[:fields],columns=columns,row_count=len(rows),first_row=rows[0],last_row=rows[-1],time_step_seconds=sorted(set((b-a).total_seconds() for a,b in zip(timestamps,timestamps[1:]))),ctd_present=all(k in columns for k in ('T','P')) and any(k in columns for k in ('C','S')))
 elif lines[0].startswith('#'):
  measurements=[line for line in lines if re.match(r'N[0-9]+ ',line)]
  fields=sorted(set(k for line in measurements for k in re.findall(r'([A-Za-z]+)[+-]?[0-9]',line)))
  entry.update(format='apb5_legacy_tagged',row_count=len(measurements),tags=fields,metadata=[line for line in lines if not re.match(r'N[0-9]+ ',line)],first_row=measurements[0],last_row=measurements[-1])
 elif lines[0].startswith('From file:'):
  i=next(i for i,line in enumerate(lines) if line.startswith('Ser;Meas;'));columns=lines[i].split(';');rows=[line.split(';') for line in lines[i+1:] if line.strip()]
  assert all(len(row)==len(columns) for row in rows)
  entry.update(format='sd200w_export_list',columns=columns,row_count=len(rows),metadata=lines[:i],first_row=dict(zip(columns,rows[0])),last_row=dict(zip(columns,rows[-1])),decimal_separator=',')
 else:raise ValueError('Unknown example: '+path.name)
 reports.append(entry)
# Fixed record observations verified against the supplied exported test.txt, not yet a general decoder.
sd=(ROOT/'data/test.SD2').read_bytes();op=(ROOT/'data/test.OP2').read_bytes();rf=(ROOT/'data/test.RF2').read_bytes();count=(len(sd)-52)//52
assert len(sd)==52+count*52 and len(op)==count*8
records=[]
for i in range(count):
 row=sd[52+i*52:104+i*52];y,month,day,hour,minute,second,interval,number=struct.unpack_from('<6BHI',row)
 sal,cond,temp,press,sound=struct.unpack_from('<5d',row,12);f,t=struct.unpack_from('<2f',op,i*8)
 records.append(dict(year_byte=y,month=month,day=day,time=f'{hour:02}:{minute:02}:{second:02}',interval=interval,number=number,salinity=sal,conductivity=cond,temperature=temp,pressure=press,sound_velocity=sound,op2_values=[f,t]))
assert abs(records[0]['temperature']-24.112)<1e-9 and records[-1]['number']==7
report=dict(text_files=reports,binary_example=dict(files=['test.SD2','test.RF2','test.OP2'],sizes=[len(sd),len(rf),len(op)],instrument_serial=struct.unpack_from('<H',sd,2)[0],observed_sd2_header_bytes=52,observed_sd2_record_bytes=52,observed_op2_record_bytes=8,row_count=count,records=records),notes=['Inventory only: logger import is not implemented in the executable.','Par, OxR and Tilt are preserved by name; units and sensor meanings need confirmation.','OSU107 row timestamps have 4 seconds between first two rows, then 2 seconds. Do not replace them with a uniform interval.','OSU107 CTD GMT header and logger LT row timestamps must remain separately identified.'])
(ROOT/'analysis/import_format_inventory.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
for item in reports:print(item['file'],item['format'],item['row_count'])
print('Binary example',count,'rows; first temperature',records[0]['temperature'])
