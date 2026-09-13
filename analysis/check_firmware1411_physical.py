"""Authorized GUI firmware test: SN107 / COM11 only. --install permits P-to-R FWU."""
from pathlib import Path
import json,hashlib,time,sys,re
from serial.tools import list_ports
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'analysis/runtime_test/firmware1411/physical';OUT.mkdir(parents=True,exist_ok=True)
run=OUT/str(time.time_ns());run.mkdir()
port=next(p for p in list_ports.comports() if p.device=='COM11')
assert port.serial_number=='OSU107-SN0107',port
config=Path('E:/config');ini=(config/'system.ini').read_text(encoding='utf-8-sig')
assert re.search(r'^serial=107$',ini,re.M) and re.search(r'^hw_rev=3\.1\.2$',ini,re.M)
original={str(p.relative_to(config)):p.read_bytes() for p in config.rglob('*') if p.is_file()}
for name,data in original.items():
 target=run/'config_before'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
# Existing update/osu_m_update.bin may be overwritten by explicit user instruction.
manifest=json.loads((ROOT/'analysis/single_exe_1411_manifest.json').read_text())
assert hashlib.sha256((ROOT/manifest['output']).read_bytes()).hexdigest()==manifest['sha256']
report={'build':manifest,'run':str(run),'mode':'install' if '--install' in sys.argv else 'check-only','before_hashes':{k:hashlib.sha256(v).hexdigest() for k,v in original.items()},'events':[]}
def record(**event):
 report['events'].append(dict(at=time.time(),**event));(run/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(event),flush=True)
from native1411_gui_support import *
from capture_window import capture as owned_capture
u.IsWindowEnabled.argtypes=[w.HWND];u.IsWindow.argtypes=[w.HWND]
def field(h,id):
 b=c.create_unicode_buffer(200000);u.SendMessageW(u.GetDlgItem(h,id),0xd,len(b),c.addressof(b));return b.value
def read(a,size=4):
 b=c.create_string_buffer(size);assert k.ReadProcessMemory(pi.process,a,b,size,None);return b.raw
def d(a):return int.from_bytes(read(a),'little')
def button(h,label):
 match=next(ch for ch,t,cl,i in children(h) if t.replace('&','')==label);u.PostMessageW(match,0xf5,0,0);time.sleep(.3)
busy=False
try:
 main=waitfor('TForm1');time.sleep(2)
 for h,t,cl in windows():
  if cl=='SITSoftwareUpdate':click(h,306)
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0
 base=d(peb.value+8);form=d(base+0x1c8964);comm=d(form+0x510)
 active_port=read(comm+0x34,1)[0];record(active_port=active_port,open_flag=read(comm+0x24,1).hex())
 if active_port!=11:
  button(main,'Setup');setup=d(d(base+0x1b1b58));sh=d(setup+0x14c);combo=d(d(setup+0x2f8)+0x14c)
  values=[]
  for i in range(u.SendMessageW(combo,0x146,0,0)):
   b=c.create_unicode_buffer(500);u.SendMessageW(combo,0x148,i,c.addressof(b));values.append(b.value)
  idx=next(i for i,v in enumerate(values) if v.upper()=='COM11');u.SendMessageW(combo,0x14e,idx,0);button(sh,'OK');time.sleep(1)
 assert read(comm+0x34,1)==bytes([11]),'COM11 was not selected'
 assert read(form+0xb15,1)==b'\x00', 'Expected native terminal mode'
 def terminal_text():
  rows=d(form+0xc14);items=d(rows+12);count=d(rows+16)
  assert count<100000
  result=[]
  for i in range(count):
   value=d(items+8*i)
   if not value:result.append('');continue
   size=d(value-4);assert size<1000000
   result.append(read(value,size).decode('latin1'))
  return result
 terminal_before=terminal_text()
 record(terminal_text_before=terminal_before)
 click(main,0x7e51);dialog=waitfor('SITFirmwareUpdate');click(dialog,504)
 u.IsWindowVisible.argtypes=[w.HWND]
 assert u.IsWindowVisible(u.GetDlgItem(dialog,508)), 'Progress indicator is missing during check'
 assert 'Please wait' in field(dialog,509),field(dialog,509)
 assert not u.IsWindowEnabled(u.GetDlgItem(dialog,506))
 owned_capture(dialog,run/'progress.png',2)
 time.sleep(.4);owned_capture(dialog,run/'progress_next.png',2)
 record(progress_indicator_visible=True,elapsed_text=field(dialog,509),close_disabled_while_busy=True)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline and not u.IsWindowEnabled(u.GetDlgItem(dialog,504)):time.sleep(.2)
 status=field(dialog,501);notes=field(dialog,502);record(check_status=status,notes=notes)
 assert not u.IsWindowVisible(u.GetDlgItem(dialog,508)), 'Progress indicator did not stop'
 owned_capture(dialog,run/'check.png',2)
 terminal_after=terminal_text()
 assert terminal_after==terminal_before, (terminal_before,terminal_after)
 record(internal_menu_hidden=True,terminal_unchanged=True)
 expected='R' if '--expect-r' in sys.argv else 'P'
 assert 'OSU107 SN107' in status and 'Installed firmware: 0.9.9'+expected in status,(status,notes)
 assert ('No newer firmware available. Server version: 0.9.9r' if expected=='R' else 'New firmware available: 0.9.9r') in status,(status,notes)
 assert 'Changes from 0.9.9Q to 0.9.9R' in notes
 assert not re.search(r'ctrl[ +_-]*t|\b(?:fwust|cfg|slp|fwupdate|fwuclr)\b',notes,re.I), 'Service instructions leaked in release notes'
 assert bool(u.IsWindowEnabled(u.GetDlgItem(dialog,505)))==(expected=='P')
 if expected=='R':assert 'Verified: device version, system.ini and firmware cleanup.' in status
 if '--install' not in sys.argv:
  report['passed']=True;record(check_passed=True,no_fwu_sent=True)
 else:
  click(dialog,505);confirmation=waitfor('#32770','Update device firmware')
  body='\n'.join(t for h,t,cl,i in children(confirmation) if cl=='Static');record(confirmation=body)
  assert '0.9.9P -> 0.9.9r' in body and 'only config/system.ini' in body and 'Do not unplug USB' in body
  owned_capture(confirmation,run/'confirmation.png',2)
  busy=True;click(confirmation,6) # IDYES: expressly authorized physical P-to-R test
  deadline=time.monotonic()+480;previous='';message=None
  while time.monotonic()<deadline:
   status=field(dialog,501)
   assert terminal_text()==terminal_before, 'Internal firmware traffic appeared in the terminal during update'
   if status!=previous:record(progress=status,detail=field(dialog,502),backup=field(dialog,507));previous=status
   boxes=[h for h,t,cl in windows() if cl=='#32770']
   if boxes:message=boxes[0];break
   if u.IsWindowEnabled(u.GetDlgItem(dialog,506)):busy=False;break
   time.sleep(.25)
  if message:
   body='\n'.join(t for h,t,cl,i in children(message) if cl=='Static');record(completion=body);owned_capture(message,run/'completion.png',2)
   assert 'Firmware update successful.' in body,body
   click(message,1);time.sleep(.5);busy=False
  else:raise AssertionError((field(dialog,501),field(dialog,502)))
  assert terminal_text()==terminal_before, 'Internal firmware traffic remained in terminal history'
  record(internal_menu_hidden_throughout_update=True)
  after={str(p.relative_to(config)):p.read_bytes() for p in config.rglob('*') if p.is_file()}
  for name,data in after.items():
   target=run/'config_after'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  assert re.search(rb'^sw_ver=0\.9\.9[Rr]\r?$',after['system.ini'],re.M)
  assert all(after.get(name)==data for name,data in original.items() if name.lower()!='system.ini')
  assert not any(Path('E:/update').iterdir())
  report['passed']=True;record(physical_update_passed=True,other_config_unchanged=True,update_folder_empty=True)
except Exception as e:
 record(error=str(e),busy=busy)
 raise
finally:
 if not busy:
  k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
 else:record(process_left_running=True,pid=pi.pid,reason='Do not terminate while update status may be in progress')
