"""Authorized COM7 diagnostic: native UART, wake I every >=50 ms; stop TX on RX."""
from pathlib import Path
import serial,time,json,sys
log=[];start=time.monotonic();last_rx=start;last_tx=0;buf=b'';phase='listen'
try:
 with serial.Serial('COM7',9600,bytesize=7,parity='E',stopbits=1,timeout=.005,write_timeout=.5,rtscts=False,dsrdtr=False,xonxoff=False) as s:
  while time.monotonic()-start<15:
   b=s.read(4096);now=time.monotonic()
   if b:
    buf+=b;last_rx=now;log.append(dict(t=round(now-start,4),rx=b.decode('ascii',errors='replace')))
   cmd=None
   if not buf and now-start>1 and now-last_tx>=.05 and phase in ('listen','wake') and now-start<10:cmd='I';phase='wake'
   if buf and now-last_rx>=.3:
    lower=buf.lower()
    if b'Start via key-board' in buf and b'Exit (passive)' in buf:phase='main';break
    if b'Status/Start/Menu' in buf and (b'measurement will start in 10 sec.' in lower or b'instrument will go passive in 10 sec.' in lower):cmd='S';phase='status'
    elif b'Current set up:' in buf and b'Measuring interval' in buf and b'Change: Y/N Menu: <G>' in buf:cmd='G';phase='menu'
    elif b'Press <M> for menu or wait 10sec' in buf:cmd='M';phase='menu'
    elif any(x.startswith(b'N') and x[1:2].isdigit() for x in buf.splitlines()) and phase!='stopping':cmd='I';phase='stopping'
   if cmd:
    s.write(cmd.encode('ascii'));last_tx=time.monotonic();log.append(dict(t=round(last_tx-start,4),tx=cmd));buf=b''
  if '--passive' in sys.argv and phase=='main':
   time.sleep(.3);s.write(b'H');log.append(dict(t=round(time.monotonic()-start,4),tx='H'));buf=b'';end=time.monotonic()+2
   while time.monotonic()<end:
    b=s.read(4096)
    if b:buf+=b;log.append(dict(t=round(time.monotonic()-start,4),rx=b.decode('ascii',errors='replace')))
   assert b'- passive -' in buf,repr(buf)
   phase='passive'
finally:
 report=dict(port='COM7',uart='9600 7E1',final_phase=phase,events=log)
 Path('analysis/com7_native_wake_probe.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
