"""Exercise the built GUI using owned window messages and an isolated file transport."""
from pathlib import Path
import subprocess,sys,json,time,csv,io,hashlib,ctypes as c
R=Path(__file__).resolve().parents[1];helper=R/'analysis/inspect_studio_live.py';out=R/'saiv-studio/test-results/v030';out.mkdir(parents=True,exist_ok=True)
checks=[]
def run(*args):
 p=subprocess.run([sys.executable,str(helper),*map(str,args)],cwd=R,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stderr)
 return json.loads(p.stdout) if p.stdout.startswith('[') else p.stdout
def check(value,name):
 if not value:raise AssertionError(name)
 checks.append(name)
 (out/'gui_progress.json').write_text(json.dumps({'checks_passed':checks},indent=2))
def expect_wire(expected,name):
 end=time.monotonic()+4
 while time.monotonic()<end and (out/'wire.bin').read_bytes()!=expected:time.sleep(.05)
 time.sleep(.3)
 check((out/'wire.bin').read_bytes()==expected,name)
def image(name):run('snapshot',name)
def read_csv(path):
 lines=path.read_text(encoding='utf-8-sig').splitlines();return list(csv.DictReader((line for line in lines if not line.startswith('#')),delimiter=';'))
def save(name):
 path=out/(name+'_'+str(time.time_ns())+'.csv');run('click',630,103);run('file',path);check(path.is_file(),'CSV Save writes '+name);return path
try:
 run('start','--demo');expected=b'ISm\r\x08\x13\x11\x7f';run('chars',expected.decode('ascii'));wire=out/'wire.bin';expect_wire(expected,'direct startup typing and exact control bytes')
 image('terminal');run('click',1060,650);image('setup');run('chars','Z');expect_wire(expected,'Setup does not transmit characters');run('click',625,568);run('chars','Q');expected+=b'Q';expect_wire(expected,'terminal regains focus after Setup')
 run('click',945,62);run('chars','X');expect_wire(expected,'measurement view does not transmit');image('measurement_list')
 run('click',384,103);image('time_graphs');run('click',473,103);image('profiles');run('click',553,103);image('multigraph')
 path=save('demo');rows=read_csv(path);check(len(rows)==240 and rows[0]['T']=='14','CSV Save keeps demo rows and values')
 run('click',925,62)
 for attempt in range(3):
  state=run('click',1060,203)
  if any(w['cls']=='#32770' for w in state):break
 state=run('file',R/'saiv-studio/tests/fixtures/logger.txt')
 if any(w['cls']=='#32770' for w in state):state=run('dialog_button',7) # Review choices instead of reusing an earlier test preset.
 for page in range(7):
  check(any(w['cls']=='SITImportChoices' for w in state),'conversion page '+str(page+1))
  if page in (0,1):run('combo',1)
  image('convert_'+str(page+1));state=run('caption','Next >')
 check(not any(w['cls']=='SITImportChoices' for w in state),'conversion completes all seven fields');image('converted_table')
 path=save('converted');rows=read_csv(path);check(len(rows)==79,'GUI conversion keeps 79 measurement rows');check('S' in rows[0] and 'T_degF' in rows[0] and 'OxR' in rows[0],'GUI conversion includes salinity, Fahrenheit and original RINKO');check(abs(float(rows[0]['T_degF'])-73.4)<1e-9 and rows[0]['T']=='23.000','GUI Fahrenheit calculation keeps original Celsius')
 run('click',925,62);state=run('click',1060,247);check(any(w['cls']=='SITMerge' for w in state),'Merge opens from terminal button');image('merge');run('caption','Close')
 run('resize',920,600);image('minimum_terminal');run('resize',1180,780);run('close')
 run('start','--open',R/'saiv-studio/tests/fixtures/reference.SD2');image('legacy_sd2');run('close')
 run('start','--open',path);image('csv_reopened');run('close')
 result={'result':'PASS','checks':checks,'exe_sha256':hashlib.sha256((R/'saiv-studio/build/SAIVStudio.exe').read_bytes()).hexdigest(),'instrument_ports_opened':0,'method':'Owned test window; pointer events use the ImGui input queue after backend refresh, enabled only by --terminal-test. WM_CHAR follows the normal foreground/popup guards. File-backed transport; no instrument port, disk update or printer output.'}
 (out/'gui_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
except Exception:
 try:image('failure')
 except Exception:pass
 raise
