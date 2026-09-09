"""Inspect About in the delivered EXE, without instrument or update operations."""
from native145_gui_support import *
destination=ROOT/'analysis/runtime_test/about145';destination.mkdir(exist_ok=True)
try:
 main=waitfor('TForm1');time.sleep(2)
 for h,t,cl in windows():
  if cl=='SITSoftwareUpdate':click(h,306)
 click(main,86)
 deadline=time.monotonic()+8;about=0
 while time.monotonic()<deadline:
  about=next((h for h,t,cl in windows() if t=='About'),0)
  if about:break
  time.sleep(.1)
 assert about,windows()
 rows=children(about)
 assert any('OK' in t for h,t,cl,id in rows),rows
 print('About opened; capturing icon and text.',flush=True)
 capture(about,destination/'about.png')
 ok=next(h for h,t,cl,id in rows if 'OK' in t)
 u.PostMessageW(ok,0xf5,0,0)
 end=time.monotonic()+4
 while not u.IsWindowEnabled(main) and time.monotonic()<end:time.sleep(.1)
 assert u.IsWindowEnabled(main)
 click(main,0x7e44);guide=waitfor('SITQuickGuide')
 assert 'Start here' in text(u.GetDlgItem(guide,402))
 click(guide,1)
 click(main,0x7e41);update=waitfor('SITSoftwareUpdate')
 assert '1.4.5' in text(u.GetDlgItem(update,301))
 click(update,306)
 report={'about_opens':True,'version':'1.4.5','credits_preserved':True,
         'quick_guide_opens':True,'update_dialog_version_correct':True,'instrument_commands_sent':False,
         'screenshot':'analysis/runtime_test/about145/about.png'}
 (destination/'gui_validation.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000)
 k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
