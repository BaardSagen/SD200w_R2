from native140_gui_support import *
from single_exe_test_support_140 import elevation
import hashlib,zipfile
folder=bundle[1];target=folder/'SAIV IT.exe';old=target.read_bytes();new=ROOT/'SAIV_Instrument_Terminal_v1.4.1_Sept2026.exe';newbytes=new.read_bytes();archive=folder/'test_release.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:z.write(new,new.name)
helper=ROOT/'analysis/single141/SIT_Update.exe';report={};children_pids=[]
def allwindows():
 rows=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if u.IsWindowVisible(h):rows.append((h,text(h),text(h,True),pid.value))
  return True
 u.EnumDesktopWindows(desk,enum,0);return rows

def run(checksum):
 args=[str(helper),str(target),str(archive),checksum,'1.4.1',new.name,hashlib.sha256(old).hexdigest(),str(bundle[0].pid),str(pi.pid),str(main)]
 import subprocess
 cmd=c.create_unicode_buffer(subprocess.list2cmdline(args));proc=PI();assert k.CreateProcessW(str(helper),cmd,None,None,False,0,None,str(folder),c.byref(si),c.byref(proc));k.CloseHandle(proc.thread);children_pids.append(proc.pid);return proc
try:
 main=waitfor('TForm1');time.sleep(1)
 failed=run('0'*64);end=time.monotonic()+20
 while time.monotonic()<end:
  boxes=[h for h,t,cl,pid in allwindows() if pid==failed.pid and cl=='#32770']
  if boxes:break
  time.sleep(.1)
 assert boxes,allwindows();body=' '.join(t for h,t,cl,id in children(boxes[0]) if cl=='Static');assert 'checksum' in body.lower(),body
 ok=next((h,id) for h,t,cl,id in children(boxes[0]) if cl=='Button' and t.replace('&','').upper()=='OK');u.SendMessageW(boxes[0],0x111,ok[1],ok[0]);k.WaitForSingleObject(failed.process,5000);k.CloseHandle(failed.process)
 assert target.read_bytes()==old and u.IsWindow(main)
 report['bad_checksum_keeps_old_program_running']=True
 installed=run(hashlib.sha256(archive.read_bytes()).hexdigest());end=time.monotonic()+35
 while time.monotonic()<end:
  if target.read_bytes()==newbytes:break
  boxes=[(h,t) for h,t,cl,pid in allwindows() if pid==installed.pid and cl=='#32770']
  if boxes:raise AssertionError([(t,children(h)) for h,t in boxes])
  time.sleep(.1)
 assert target.read_bytes()==newbytes,allwindows()
 backups=list(folder.glob('SAIV IT.exe.previous-*.bak'));assert len(backups)==1 and backups[0].read_bytes()==old
 report['same_path_replaced']=True;report['backup_byte_identical']=True
 end=time.monotonic()+25;restarted=[]
 while time.monotonic()<end:
  restarted=[(h,pid) for h,t,cl,pid in allwindows() if cl=='TForm1' and pid!=pi.pid]
  if restarted:break
  time.sleep(.2)
 assert restarted,allwindows()
 h,pid=restarted[0];process=k.OpenProcess(0x1fffff,False,pid);assert elevation(process)==0
 report['restarted_without_elevation']=True
 k.TerminateProcess(process,0);k.WaitForSingleObject(process,5000);k.CloseHandle(process)
 k.WaitForSingleObject(installed.process,5000);k.CloseHandle(installed.process)
 (ROOT/'analysis/runtime_test/update141').mkdir(exist_ok=True);(ROOT/'analysis/runtime_test/update141/install_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process)
 k.WaitForSingleObject(bundle[0].process,5000);k.CloseHandle(bundle[0].thread);k.CloseHandle(bundle[0].process)
 for h,t,cl,pid in allwindows():
  if cl=='#32770' and pid in children_pids:u.PostMessageW(h,0x10,0,0)
 u.CloseDesktop(desk)
