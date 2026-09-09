"""Authorized readback only on COM7/COM11; never writes a setting."""
import serial,time,re,json
from pathlib import Path
out=Path('analysis/runtime_test/settings139');out.mkdir(exist_ok=True);reports=[]
for port in ['COM7','COM11']:
 events=[];start=time.monotonic();buf='';last=start
 def log(**kw):events.append(dict(t=round(time.monotonic()-start,3),**kw))
 try:
  with serial.Serial(port,9600,bytesize=7 if port=='COM7' else 8,parity='E' if port=='COM7' else 'N',stopbits=1,timeout=.01,write_timeout=1,rtscts=False,dsrdtr=False,xonxoff=False) as ser:
   def tx(s):
    global buf,last
    ser.write(s.encode());log(tx=s);buf='';last=time.monotonic()
   def receive(seconds,quiet=.35):
    global buf,last
    until=time.monotonic()+seconds
    while time.monotonic()<until:
     raw=ser.read(4096)
     if raw:part=raw.decode('ascii',errors='replace');buf+=part;last=time.monotonic();log(rx=part)
     if buf and time.monotonic()-last>=quiet:return buf
    return buf
   receive(1)
   for step in range(18):
    lo=buf.lower()
    if 'start via key-board' in lo and 'exit (passive)' in lo:break
    if 'status/start/menu' in lo or 'instrument will go passive in 10 sec' in lo:tx('S');receive(3)
    elif 'current set up:' in lo and 'change: y/n menu: <g>' in lo:tx('G');receive(3)
    elif 'press <m> for menu' in lo:tx('M');receive(3)
    elif not buf or 'hold' in lo or '- passive -' in lo:
     buf=''
     for wake in range(70):
      ser.write(b'I');log(tx='I');time.sleep(.06);raw=ser.read(4096)
      if raw:buf=raw.decode('ascii',errors='replace');last=time.monotonic();log(rx=buf);receive(3);break
    else:tx('G');receive(3)
   else:raise RuntimeError('Could not reach main menu: '+buf)
   time.sleep(1);tx('I');interval_text=receive(4);assert 'y/n' in interval_text.lower(),interval_text
   match=re.search(r'Measuring interval\s*(\d+)\s*(sec|min|hour)',interval_text,re.I);assert match,interval_text;interval=int(match[1])*{'sec':1,'min':60,'hour':3600}[match[2].lower()]
   tx('G');receive(3);assert 'exit (passive)' in buf.lower()
   tx('S');clock_text=receive(4);assert 'y/n' in clock_text.lower(),clock_text
   zone=re.search(r'\b(LT|GMT)\b',clock_text);assert zone,clock_text
   tx('N');receive(3)
   report=dict(port=port,interval_seconds=interval,sd200_zone=zone[1],clock_text=clock_text,events=events)
   reports.append(report);print(json.dumps({k:v for k,v in report.items() if k!='events'},indent=2),flush=True)
 except Exception as e:reports.append(dict(port=port,error=str(e),events=events));print(port,str(e),flush=True)
 (out/'physical_preflight.json').write_text(json.dumps(reports,indent=2))
assert len(reports)==2 and not any('error' in x for x in reports)
