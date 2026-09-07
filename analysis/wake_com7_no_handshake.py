import serial,time,json
from pathlib import Path
out=bytearray();sent=bytearray()
with serial.Serial('COM7',9600,timeout=.05,write_timeout=1,rtscts=False,dsrdtr=False,xonxoff=False) as s:
 def read_for(t):
  end=time.monotonic()+t
  while time.monotonic()<end:out.extend(s.read(4096))
 read_for(.5)
 s.write(b'G');sent.extend(b'G');read_for(1)
 awake=lambda:any(x in out.lower() for x in (b'menu:',b'change air pressure',b'status/start/menu',b'change mode'))
 deadline=time.monotonic()+8
 while not awake() and time.monotonic()<deadline:
  s.write(b'I');sent.extend(b'I');read_for(.1)
 read_for(1)
r=dict(port='COM7',baud=9600,parity='None',rtscts=False,dsrdtr=False,tx=sent.decode(),rx=out.decode('latin1'),awake=awake())
Path('analysis/com7_no_handshake_wake.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
