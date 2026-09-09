from native142_gui_support import *
import json
try:
 main=waitfor('TForm1');time.sleep(2)
 found=[h for h,t,cl in windows() if cl=='SITSoftwareUpdate']
 if not found:click(main,0x7e41)
 dialog=waitfor('SITSoftwareUpdate');status=text(u.GetDlgItem(dialog,301));assert 'Installed version: 1.4.2' in status,status
 assert 'Would you like' in status
 assert not u.IsWindowEnabled(u.GetDlgItem(dialog,305))
 result={'installed_version':'1.4.2','single_exe_starts':True,'update_dialog_reports_142':True,'no_network_check_requested':True}
 (ROOT/'analysis/runtime_test/update142').mkdir(exist_ok=True)
 (ROOT/'analysis/runtime_test/update142/gui_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
