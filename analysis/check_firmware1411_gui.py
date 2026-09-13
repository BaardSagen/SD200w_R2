"""Exercise manual firmware UI in the delivered EXE; never request a device operation."""
from native1411_gui_support import *
from capture_window import capture as owned_capture
u.IsWindow.argtypes=[w.HWND];u.IsWindowEnabled.argtypes=[w.HWND]
u.MoveWindow.argtypes=[w.HWND,c.c_int,c.c_int,c.c_int,c.c_int,w.BOOL]
destination=ROOT/'analysis/runtime_test/firmware1411';destination.mkdir(exist_ok=True)
report={}
def field(h,id):
 b=c.create_unicode_buffer(200000);u.SendMessageW(u.GetDlgItem(h,id),0xd,len(b),c.addressof(b));return b.value
try:
 main=waitfor('TForm1');time.sleep(2)
 assert not any(cl=='SITFirmwareUpdate' for h,t,cl in windows())
 report['no_firmware_startup_window']=True
 for h,t,cl in windows():
  if cl=='SITSoftwareUpdate':click(h,306)
 labels=menus(u.GetMenu(main));assert sum(id==0x7e51 for label,id in labels)==1
 assert any('Firmware' in label and id==0x7e51 for label,id in labels)
 assert any('Quick guide' in label and id==0x7e44 for label,id in labels)
 assert any('Update software' in label and id==0x7e41 for label,id in labels)
 report['help_menu']=labels[-6:]
 click(main,0x7e51);dialog=waitfor('SITFirmwareUpdate')
 assert not u.IsWindowEnabled(main)
 assert 'connected to this PC and SIT' in field(dialog,501)
 assert 'Would you like to check' in field(dialog,501)
 assert 'No firmware server is contacted' in field(dialog,502)
 assert not u.IsWindowEnabled(u.GetDlgItem(dialog,505))
 owned_capture(dialog,destination/'manual_prompt.png',2)
 report['manual_prompt']=field(dialog,501);report['update_disabled_before_check']=True
 u.MoveWindow(dialog,60,60,680,490,True);time.sleep(.2);owned_capture(dialog,destination/'minimum_size.png',2)
 click(dialog,506);time.sleep(.2);assert not u.IsWindow(dialog) and u.IsWindowEnabled(main)
 click(main,0x7e51);dialog=waitfor('SITFirmwareUpdate');assert not u.IsWindowEnabled(u.GetDlgItem(dialog,505))
 # Assert the native port is closed before testing the missing-connection error.
 # Simulate a closed-port flag in the owned process if startup opened the port.
 def read(a,size=4):
  b=c.create_string_buffer(size);assert k.ReadProcessMemory(pi.process,a,b,size,None);return b.raw
 def d(a):return int.from_bytes(read(a),'little')
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0
 base=d(peb.value+8);form=d(base+0x1c8964);comm=d(form+0x510)
 saved_open=read(comm+0x24,1) if comm else b'\x00'
 if comm and saved_open!=b'\x00':
  # Only an in-memory flag in this owned test process is changed. No ClosePort,
  # Detect, device command or disk write is requested by the missing-port test.
  k.WriteProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.c_void_p]
  assert k.WriteProcessMemory(pi.process,comm+0x24,b'\x00',1,None)
  report['missing_connection_simulated_in_owned_process']=True
 try:
  click(dialog,504);time.sleep(.5)
  assert 'Connect the logger in SIT first' in field(dialog,502),field(dialog,502)
  assert not u.IsWindowEnabled(u.GetDlgItem(dialog,505))
  owned_capture(dialog,destination/'missing_connection.png',2)
  report['missing_connection_blocks_update']=True
 finally:
  if comm and saved_open!=b'\x00':assert k.WriteProcessMemory(pi.process,comm+0x24,saved_open,1,None)
 u.PostMessageW(dialog,0x10,0,0);time.sleep(.3);assert not u.IsWindow(dialog) and u.IsWindowEnabled(main)
 click(main,0x7e44);guide=waitfor('SITQuickGuide');assert 'Start' in field(guide,402)
 u.PostMessageW(guide,0x10,0,0);time.sleep(.3)
 click(main,0x7e41);software=waitfor('SITSoftwareUpdate');assert '1.4.11' in field(software,301);click(software,306)
 report['guide_and_software_update_preserved']=True
 report['no_firmware_commands']=True
 (destination/'gui_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
