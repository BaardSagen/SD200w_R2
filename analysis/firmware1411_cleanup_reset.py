"""One user-authorized cleanup reset on SN107 COM11. Never sends FWU or deletes files."""
import serial,time,json,re,hashlib
from pathlib import Path
from serial.tools import list_ports
assert next(p for p in list_ports.comports() if p.device=='COM11').serial_number=='OSU107-SN0107'
out=Path('analysis/runtime_test/firmware1411/physical')/('cleanup-reset-'+str(time.time_ns()));out.mkdir(parents=True,exist_ok=True)
f=Path('E:/update/osu_m_update.bin');old=f.read_bytes();(out/'existing_osu_m_update.bin').write_bytes(old)
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
 assert 'OSU107, SN: 107, ver-0.9.9P' in menu and 'HW: OSU-M rev-3.1.2' in menu
 send('CFG\r',lambda s:'[Config]>' in s)
 send('FWUST\r',lambda s:'[Config]>' in s)
 send('Q\r',lambda s:'Returning to main menu' in s)
 send('\x14\r',lambda s:'DEACTIVATED' in s and 'to reactivate.' in s)
 send('SLP\r',lambda s:'[Sleep]>' in s)
 event(tx='RESET\r');ser.write(b'RESET\r');ser.flush()
start=time.monotonic();gone=False
while time.monotonic()-start<90:
 ports=[p for p in list_ports.comports() if p.device=='COM11']
 if not ports:gone=True
 if gone and ports and Path('E:/config/system.ini').exists():
  time.sleep(3);event(returned=True,seconds=round(time.monotonic()-start,1),update_file_still_present=f.exists(),update_contents=[p.name for p in Path('E:/update').iterdir()] if Path('E:/update').exists() else []);break
 time.sleep(.25)
else:raise RuntimeError('COM11/disk did not return after reset')
