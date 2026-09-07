import serial,time,json
from pathlib import Path
r=[]
with serial.Serial('COM7',9600,timeout=.1,write_timeout=1) as s:
 def listen(seconds):
  end=time.monotonic()+seconds;b=bytearray()
  while time.monotonic()<end:b.extend(s.read(4096))
  return b.decode('latin1')
 r.append({'rx':listen(2)})
 s.write(b'G');r.append({'tx':'G','rx':listen(3)})
 s.write(b'H');r.append({'tx':'H','rx':listen(4)})
Path('analysis/sd200_passive_preparation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
