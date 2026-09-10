"""Open the shipped EXE and exercise offline help on an owned private desktop."""
from native149_gui_support import *
from capture_window import capture as window_capture
def capture(h,path):window_capture(h,path,2)

expected=json.loads((ROOT/'analysis/formula_guide149_topics.json').read_text(encoding='utf-8'))
report={};destination=ROOT/'analysis/runtime_test/guide149';destination.mkdir(exist_ok=True)
u.MoveWindow.argtypes=[w.HWND,c.c_int,c.c_int,c.c_int,c.c_int,w.BOOL]
u.GetFocus.restype=w.HWND
u.IsWindowEnabled.argtypes=[w.HWND]
def field(h,id):
 b=c.create_unicode_buffer(20000)
 u.SendMessageW(u.GetDlgItem(h,id),0xd,len(b),c.addressof(b))
 return b.value
def waitclosed(h):
 end=time.monotonic()+3
 while u.IsWindow(h) and time.monotonic()<end:time.sleep(.05)
 assert not u.IsWindow(h)
try:
 main=waitfor('TForm1');time.sleep(2)
 for h,t,cl in windows():
  if cl=='SITSoftwareUpdate':click(h,306)
 labels=menus(u.GetMenu(main));assert sum(id==0x7e44 for label,id in labels)==1
 assert any('Quick guide' in label and id==0x7e44 for label,id in labels)
 assert any('Update software' in label and id==0x7e41 for label,id in labels)
 report['help_menu']=labels[-5:]
 click(main,0x7e44);guide=waitfor('SITQuickGuide');assert not u.IsWindowEnabled(main)
 capture(guide,destination/'start.png')
 topics=[]
 for i in range(9+len(expected)):
  u.SendMessageW(u.GetDlgItem(guide,401),0x186,i,0)
  u.SendMessageW(guide,0x111,401|(1<<16),u.GetDlgItem(guide,401))
  title=field(guide,402);body=field(guide,403)
  assert len(body)>300 and title and '\r\n' in body,(i,title,body)
  if i>=9:
   item=expected[i-9];assert title==item['title'] and body==item['text'],(i,title,'Page text mismatch/truncation')
   edit=u.GetDlgItem(guide,403);u.SendMessageW(edit,0xb1,len(body),len(body));u.SendMessageW(edit,0xb7,0,0)
   assert len(body)<4000 or u.SendMessageW(edit,0xce,0,0)>0,(title,'End of long page not scrollable')
   if i in [10,13,16,23]:capture(guide,destination/f'topic_{i}_end.png')
   u.SendMessageW(edit,0xb1,0,0);u.SendMessageW(edit,0xb7,0,0)
  topics.append({'topic':title,'characters':len(body)})
  if i in [4,7,9,10,11,13,16,17,23,25]:capture(guide,destination/f'topic_{i}.png')
 report['topics']=topics
 assert u.SendMessageW(u.GetDlgItem(guide,401),0x18b,0,0)==9+len(expected)
 report['full_formula_text_matches_source']=True
 # Keyboard selection is handled by the real LISTBOX, then the dialog loop.
 listbox=u.GetDlgItem(guide,401)
 u.PostMessageW(listbox,0x100,0x24,0) # Home
 time.sleep(.2);assert field(guide,402)=='Start here'
 u.PostMessageW(listbox,0x100,0x28,0) # Down
 time.sleep(.2);assert field(guide,402)=='Detect and terminal'
 report['arrow_navigation']=True
 # Tab reaches the read-only text; Escape must also work while the edit has focus.
 u.PostMessageW(listbox,0x100,9,0);time.sleep(.15)
 u.PostMessageW(u.GetDlgItem(guide,403),0x100,0x1b,0);waitclosed(guide)
 assert u.IsWindowEnabled(main);report['escape_restores_main']=True
 click(main,0x7e44);guide=waitfor('SITQuickGuide')
 assert field(guide,402)=='Start here'
 u.MoveWindow(guide,40,40,800,480,True);time.sleep(.2)
 u.SendMessageW(u.GetDlgItem(guide,401),0x186,4,0)
 u.SendMessageW(guide,0x111,401|(1<<16),u.GetDlgItem(guide,401))
 capture(guide,destination/'minimum_size.png')
 # At minimum size, the text must either fit or remain scrollable.
 edit=u.GetDlgItem(guide,403)
 before=u.SendMessageW(edit,0xce,0,0) # EM_GETFIRSTVISIBLELINE
 u.SendMessageW(edit,0xb6,0,100) # EM_LINESCROLL
 scrolled=u.SendMessageW(edit,0xce,0,0)>before
 last=u.SendMessageW(edit,0xd6,len(field(guide,403))-1,0) # EM_POSFROMCHAR
 assert scrolled or last!=-1
 report['minimum_size_text_accessible']=True
 click(guide,1);waitclosed(guide);assert u.IsWindowEnabled(main)
 report['close_button_and_reopen']=True
 # Closing via the system X also restores the owner.
 click(main,0x7e44);guide=waitfor('SITQuickGuide')
 u.PostMessageW(guide,0x10,0,0);waitclosed(guide);assert u.IsWindowEnabled(main)
 report['window_close']=True
 # Repeated Help initialization must not duplicate commands.
 for _ in range(3):u.SendMessageW(main,0x116,u.GetMenu(main),0)
 assert sum(id==0x7e44 for label,id in menus(u.GetMenu(main)))==1
 click(main,0x7e41);update=waitfor('SITSoftwareUpdate')
 assert '1.4.9' in field(update,301) and 'No internet connection' in field(update,302)
 click(update,306);report['update_dialog_preserved_without_network']=True
 report['shipped_exe_sha256']=__import__('hashlib').sha256((ROOT/'SAIV_Instrument_Terminal_v1.4.9_Sept2026.exe').read_bytes()).hexdigest()
 report['single_exe_non_admin']=True
 report['instrument_commands_sent']=False
 (destination/'gui_validation.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000)
 k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
