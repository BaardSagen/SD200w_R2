"""Bounded COM7 diagnostic explicitly requested by user; never starts/erases/calibrates."""
import serial,time,json
from pathlib import Path
log=[];start=time.monotonic();last_rx=-100;buffer=b''
def stamp():return round(time.monotonic()-start,3)
def mode():
 t=buffer.lower()
 if b'start via key-board' in t and b'exit (passive)' in t and b'<h>' in t:return 'main'
 if b'status/start/menu' in t and b'measurement will start in 10 sec.' in t:return 'startup'
 if b'<i>' in t and b'<m>' in t and b'start' in t and b'coefficients' not in t and b'interval' not in t:return 'status'
 if b' t' in t and b' p' in t and any(x.startswith(b'N') and x[1:2].isdigit() for x in buffer.splitlines()):return 'measuring'
 return 'unknown'
def encoded(s):return bytes((c&127)|(((c&127).bit_count()%2)<<7) for c in s)
try:
 with serial.Serial('COM7',9600,timeout=.02,write_timeout=.5,rtscts=False,dsrdtr=False,xonxoff=False) as port:
  def read_for(seconds):
   global buffer,last_rx
   end=time.monotonic()+seconds
   while time.monotonic()<end:
    raw=port.read(4096)
    if raw:last_rx=time.monotonic();buffer+=bytes(c&127 for c in raw);log.append(dict(t=stamp(),rx_hex=raw.hex(),text=bytes(c&127 for c in raw).decode('ascii',errors='replace')))
  def send(s):
   global buffer
   assert time.monotonic()-last_rx>=.25
   wire=encoded(s);port.write(wire);log.append(dict(t=stamp(),tx=s.decode(),wire_hex=wire.hex()));buffer=b''
  read_for(1.2)
  if not buffer:
   send(b'G');read_for(1.1)
  if not buffer:
   # Reproduce the current slow wake cadence for a bounded interval.
   end=time.monotonic()+2.8
   while not buffer and time.monotonic()<end:send(b'I');read_for(.3)
  if not buffer:
   # Test keyboard-like repeat, stopping at the very first response byte.
   log.append(dict(t=stamp(),phase='100ms repeat'))
   end=time.monotonic()+8
   while not buffer and time.monotonic()<end:send(b'I');read_for(.1)
  for attempt in range(4):
   end=time.monotonic()+3
   while time.monotonic()<end:
    read_for(.03)
    if buffer and time.monotonic()-last_rx>=.3:break
   state=mode();log.append(dict(t=stamp(),state=state,buffer=buffer.decode('ascii',errors='replace')))
   if state=='startup':send(b'S')
   elif state=='status':send(b'M')
   else:break
except Exception as e:log.append(dict(error=str(e)))
report=dict(port='COM7',physical='9600 8N1',logical='7E1 software',events=log)
Path('analysis/com7_wake_timing_20260908.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
