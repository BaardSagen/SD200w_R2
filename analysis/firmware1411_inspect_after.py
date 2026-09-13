"""Read-only post-FWU inspection on SN107 COM11. No FWU/reset/delete."""
import serial,time,json,re,hashlib
from pathlib import Path
from serial.tools import list_ports
assert next(p for p in list_ports.comports() if p.device=='COM11').serial_number=='OSU107-SN0107'
out=Path('analysis/runtime_test/firmware1411/physical')/('inspect-after-'+str(time.time_ns()));out.mkdir(parents=True,exist_ok=True)
f=Path('E:/update/osu_m_update.bin')
if f.exists(): (out/'existing_osu_m_update.bin').write_bytes(f.read_bytes())
log=[]
def event(**kw):log.append(dict(at=time.time(),**kw));(out/'transcript.json').write_text(json.dumps(log,indent=2));print(json.dumps(kw),flush=True)
with serial.Serial('COM11',9600,bytesize=8,parity='N',stopbits=1,timeout=.03,write_timeout=2) as ser:
 def receive(predicate,timeout=15):
  text='';last=time.monotonic();until=last+timeout
  while time.monotonic()<until:
   raw=ser.read(4096)
   if raw:text+=raw.decode('ascii',errors='replace');last=time.monotonic()
   if predicate(text) and time.monotonic()-last>=.3:event(rx=text);return text
  event(rx=text);raise RuntimeError('Incomplete response')
 def send(cmd,predicate):
  event(tx=cmd);ser.write(cmd.encode('ascii'));ser.flush();return receive(predicate)
 time.sleep(.5);ser.reset_input_buffer()
 send('\x14\r',lambda s:'DEACTIVATED' in s and 'to reactivate.' in s)
 menu=send('M\r',lambda s:'> to execute Leds.' in s)
 assert 'OSU107, SN: 107, ver-0.9.9R' in menu and 'HW: OSU-M rev-3.1.2' in menu
 ver=send('VER\r',lambda s:'Build:' in s)
 assert 'ver-0.9.9R' in ver
 send('CFG\r',lambda s:'[Config]>' in s)
 status=send('FWUST\r',lambda s:'[Config]>' in s)
 assert 'FWU write lock: CLEAR' in status
 send('Q\r',lambda s:'Returning to main menu' in s)
event(inspected=True,update_file_still_present=f.exists())
