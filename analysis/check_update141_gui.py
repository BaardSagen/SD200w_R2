import winreg,time,json
KEY=r'Software\MHP\SdInstr\SoftwareUpdate';NAME='DisableStartupCheck'
key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,KEY)
try:old=winreg.QueryValueEx(key,NAME)
except FileNotFoundError:old=None
winreg.SetValueEx(key,NAME,0,winreg.REG_DWORD,0)
from native141_gui_support import *
report={}
def field(h,id):
 b=c.create_unicode_buffer(150000);u.SendMessageW(u.GetDlgItem(h,id),0xd,len(b),c.addressof(b));return b.value
try:
 main=waitfor('TForm1');dialog=waitfor('SITSoftwareUpdate',timeout=15)
 initial=text(u.GetDlgItem(dialog,301));notes=field(dialog,302);assert 'Would you like' in initial and 'No internet connection' in notes
 report['startup_prompt_before_network']=True
 assert any('Update software' in label for label,id in menus(u.GetMenu(main)))
 report['help_menu']=True
 click(dialog,304)
 end=time.monotonic()+50
 while time.monotonic()<end:
  status=text(u.GetDlgItem(dialog,301))
  if 'No newer version' in status:break
  time.sleep(.2)
 assert 'Server version: 1.4.0' in status,status
 assert 'CLOCK CORRECTION IN 1.4.0' in field(dialog,302),repr(field(dialog,302))
 assert not u.IsWindowEnabled(u.GetDlgItem(dialog,305))
 report['live_server']=status;report['readme_shown']=True;report['older_server_not_offered']=True
 u.SendMessageW(u.GetDlgItem(dialog,303),0xf5,0,0);time.sleep(.2)
 assert winreg.QueryValueEx(key,NAME)[0]==1
 click(dialog,306);time.sleep(.2)
 click(main,0x7e41);dialog=waitfor('SITSoftwareUpdate');assert u.SendMessageW(u.GetDlgItem(dialog,303),0xf0,0,0)==1
 report['manual_check_while_disabled']=True
 # Check preference across a fresh delivered-EXE launch.
 click(dialog,306);k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle)
 pi,bundle=start(si,desk,out);import native141_gui_support as support;support.pi=pi;main=waitfor('TForm1');time.sleep(3)
 assert not any(cl=='SITSoftwareUpdate' for h,t,cl in windows())
 report['disabled_persists_after_restart']=True
 click(main,0x7e41);dialog=waitfor('SITSoftwareUpdate');u.SendMessageW(u.GetDlgItem(dialog,303),0xf5,0,0);assert winreg.QueryValueEx(key,NAME)[0]==0
 report['can_reenable']=True
 print(json.dumps(report,indent=2),flush=True)
 (ROOT/'analysis/runtime_test/update141').mkdir(exist_ok=True)
 (ROOT/'analysis/runtime_test/update141/gui_validation.json').write_text(json.dumps(report,indent=2))
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
 if old is None:winreg.DeleteValue(key,NAME)
 else:winreg.SetValueEx(key,NAME,0,old[1],old[0])
 winreg.CloseKey(key)
