# Compile the isolated old-version test client from the same update UI source.
import subprocess,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
subprocess.run(['g++','-std=c++11','-O2','-mwindows','-static',str(root/'analysis/test_update141_host.cpp'),str(root/'analysis/single141/helper_resource.o'),'-lcomctl32','-lgdi32','-lwininet','-ladvapi32','-lshell32','-o',str(root/'analysis/test_update141_host.exe')],check=True)
from native141_gui_support import *
import native141_gui_support as support
from single_exe_test_support_141 import descendants
import os,shutil,hashlib
k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle)
folder=out/('server upgrade test '+str(time.time_ns()));folder.mkdir();target=folder/'Field station.exe';shutil.copyfile(ROOT/'analysis/test_update141_host.exe',target);old=target.read_bytes();previous=os.environ.get('SIT_UPDATE_HELPER');os.environ['SIT_UPDATE_HELPER']=str(ROOT/'analysis/single141/SIT_Update.exe')
pi=PI();assert k.CreateProcessW(str(target),None,None,None,False,0,None,str(folder),c.byref(si),c.byref(pi));k.CloseHandle(pi.thread);support.pi=pi
if previous is None:del os.environ['SIT_UPDATE_HELPER']
else:os.environ['SIT_UPDATE_HELPER']=previous
owned={pi.pid}
def track():
 for parent in list(owned):owned.update(descendants(parent))
def allwindows():
 track();rows=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if pid.value in owned and u.IsWindowVisible(h):rows.append((h,text(h),text(h,True),pid.value))
  return True
 u.EnumDesktopWindows(desk,enum,0);return rows
try:
 dialog=waitfor('SITSoftwareUpdate');click(dialog,304);end=time.monotonic()+40
 while time.monotonic()<end:
  status=text(u.GetDlgItem(dialog,301));track()
  if 'New version available: 1.4.0' in status:break
  time.sleep(.1)
 assert 'New version available: 1.4.0' in status,status
 assert u.IsWindowEnabled(u.GetDlgItem(dialog,305))
 click(dialog,305);confirm=waitfor('#32770','Install SAIV IT update');u.SendMessageW(confirm,0x111,7,0);time.sleep(.3);assert target.read_bytes()==old and u.IsWindow(dialog)
 click(dialog,305);confirm=waitfor('#32770','Install SAIV IT update');u.SendMessageW(confirm,0x111,6,0)
 expected=(ROOT/'SAIV_Instrument_Terminal_v1.4.0_Sept2026.exe').read_bytes();end=time.monotonic()+60
 while time.monotonic()<end:
  track()
  if target.read_bytes()==expected:break
  errors=[h for h,t,cl,pid in allwindows() if cl=='#32770' and t=='SAIV IT update not installed']
  if errors:raise AssertionError(children(errors[0]))
  time.sleep(.1)
 assert target.read_bytes()==expected,allwindows()
 backups=list(folder.glob('Field station.exe.previous-*.bak'));assert len(backups)==1 and backups[0].read_bytes()==old
 end=time.monotonic()+20;restarted=[]
 while time.monotonic()<end:
  restarted=[(h,pid) for h,t,cl,pid in allwindows() if cl=='TForm1']
  if restarted:break
  time.sleep(.2)
 assert restarted,allwindows()
 report={'test_client_version':'1.3.9','live_server_version':'1.4.0','newer_offer_shown':True,'confirmation_no_preserves_program':True,'confirmation_yes_downloads_verifies_installs':True,'same_custom_filename':target.name,'backup_matches_original':True,'restarted':True,'downloaded_exe_sha256':hashlib.sha256(expected).hexdigest()}
 (ROOT/'analysis/runtime_test/update141/server_install_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
finally:
 track();k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process)
 for pid in owned-{pi.pid}:
  proc=k.OpenProcess(0x1fffff,False,pid)
  if proc:k.TerminateProcess(proc,0);k.WaitForSingleObject(proc,5000);k.CloseHandle(proc)
 u.CloseDesktop(desk)
