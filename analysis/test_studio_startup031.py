"""Regression for normal, empty startup: measure the rendered terminal rectangle."""
from pathlib import Path
import subprocess,sys,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];OUT=R/'saiv-studio/test-results/v031';OUT.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run([sys.executable,str(R/'analysis/inspect_studio_live.py'),*map(str,args),'--results','v031'],cwd=R,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stderr)
 return json.loads(p.stdout) if p.stdout.startswith('[') else p.stdout
def terminal(path):
 im=Image.open(path).convert('RGB');y=im.height//2;runs=[];start=None
 for x in range(16,im.width-16):
  red,green,blue=im.getpixel((x,y));dark=red<45 and green<60 and blue<80
  if dark and start is None:start=x
  if start is not None and (not dark or x==im.width-17):runs.append((start,x));start=None
 left,right=max(runs,key=lambda p:p[1]-p[0]);return dict(window_width=im.width,left=left,width=right-left)
before=terminal(R/'saiv-studio/test-results/v031_before/start_0.png');assert before['width']<100,'Reproduction no longer has the narrow strip'
checks=[]
try:
 run('start','--normal')
 for label,width,height in [('normal_startup',1180,780),('minimum_startup',920,600),('large_startup',1450,900)]:
  run('resize',width,height);state=run('snapshot',label);window=next(w for w in state if w['cls']=='SAIVInstrumentStudio');assert '0.3.1' in window['text'];bounds=terminal(window['image']);assert bounds['left']<50 and bounds['width']>bounds['window_width']*.65,(label,bounds);checks.append(dict(test=label,**bounds))
 run('close');run('start','--normal','--demo');state=run('snapshot','demo_startup');bounds=terminal(next(w['image'] for w in state if w['cls']=='SAIVInstrumentStudio'));assert bounds['left']<50 and bounds['width']>bounds['window_width']*.65;checks.append(dict(test='demo_startup',**bounds));run('close')
except Exception:
 try:run('snapshot','failure');run('close')
 except Exception:pass
 raise
report=dict(result='PASS',version='0.3.1',before=before,checks=checks,exe_sha256=hashlib.sha256((R/'saiv-studio/build/SAIVStudio.exe').read_bytes()).hexdigest(),method='Real normal startup without --demo or --terminal-test, rendered PrintWindow capture, three sizes; separate demo regression. No instrument port opened.')
(OUT/'startup_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
