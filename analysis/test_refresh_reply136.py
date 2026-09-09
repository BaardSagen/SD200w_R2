"""Execute refresh hooks with mocked serial writes; no hardware commands."""
from pathlib import Path
import unittest
src=Path(__file__).with_name('test_guard.py').read_text().split('class GuardTests')[0]
src=src.replace("patch_manifest.json","refresh_reply_manifest.json").replace("SD200W_diskguard.exe","SD200W_SAIV_OSU107_RefreshReply.exe")
src=src.replace("ROOT/'SD200W_SAIV_OSU107_RefreshReply.exe'","ROOT/'analysis/single136/SAIV_IT_Runtime.exe'")
src=src.replace("address in {self.base+r", "self.base+0x299000 <= address < self.base+0x299090 or self.base+0x2e0000 <= address < self.base+0x2f0000 or address in {self.base+r")
exec(compile(src,'refresh_harness','exec'))
OldHarness=Harness
class Harness(OldHarness):
 def __init__(self,base=0x400000):
  super().__init__(base);self.writes=[];self.timeouts=[]
  self.put32(base+0x1c9224,self.RETURN-0x200)
  self.put32(base+0x1c9220,self.RETURN-0x300)
 def hook(self,uc,address,size,unused):
  if address==self.base+0x7ffc4:
   assert uc.reg_read(UC_X86_REG_EAX)==self.COMM
   ptr=uc.reg_read(UC_X86_REG_EDX);n=self.get32(ptr-4)
   self.writes.append(bytes(uc.mem_read(ptr,n)))
   if getattr(self,'auto_ack',True):self.state('reply_status',1)
   self.ret()
  elif address==self.RETURN-0x200:
   sp=uc.reg_read(UC_X86_REG_ESP);assert self.cstring(self.get32(sp+4))=='user32.dll'
   uc.reg_write(UC_X86_REG_EAX,123);self.ret(4)
  elif address==self.RETURN-0x300:
   sp=uc.reg_read(UC_X86_REG_ESP);assert self.cstring(self.get32(sp+8))=='MessageBoxTimeoutA'
   uc.reg_write(UC_X86_REG_EAX,self.RETURN-0x400);self.ret(8)
  elif address==self.RETURN-0x400:
   sp=uc.reg_read(UC_X86_REG_ESP)
   self.messages.append(self.cstring(self.get32(sp+8)));self.timeouts.append(self.get32(sp+24));self.ret(24)
  elif address==self.base+0x102078:
   self.ret()
  elif address==self.base+0x7bb4:
   self.sleep_count=getattr(self,'sleep_count',0)+1;self.ret(4)
  elif address==self.RETURN-0x100:
   sp=uc.reg_read(UC_X86_REG_ESP);ptr=self.get32(sp+8)
   data=bytearray()
   while self.byte(ptr):data.append(self.byte(ptr));ptr+=1
   self.messages.append(data.decode('cp1252'));self.ret(16)
  elif self.base+0x2830d9<=address<self.base+0x28314f:pass
  else:super().hook(uc,address,size,unused)
 def complete(self):return self.run(0x1a156f,[0x1a1574,0x1a1586,0x1a15c7],eax=2)
class RefreshTests(unittest.TestCase):
 def test_refresh_once_and_relocated(self):
  for base in (0x400000,0x1400000):
   h=Harness(base);h.click();h.active();h.receive('Data logged by the SAIV110 is stored on its internal disk.\r\nRefresh disk Y/N')
   self.assertEqual(h.writes,[]);self.assertEqual(h.state('pending'),1)
   self.assertEqual(h.complete(),base+0x1a15c7)
   self.assertEqual(h.writes,[b'Y']);self.assertEqual(h.messages,['Performing refresh of disks']);self.assertEqual(h.timeouts,[3000])
   h.complete();self.assertEqual(h.writes,[b'Y'])
 def test_only_specific_prompt_during_download(self):
  for prompt in ('Erase memory Y/N','Refresh disk Y/','Refresh disk Y/X','N0001 C00.000','Some other question Y/N'):
   h=Harness();h.click();h.active();h.receive(prompt);h.complete();self.assertEqual(h.writes,[])
  h=Harness();h.active();h.receive('Refresh disk Y/N');h.complete();self.assertEqual(h.writes,[])
  h=Harness();h.click(log=True);h.active(log=True);h.receive('Refresh disk Y/N');h.complete();self.assertEqual(h.writes,[])
 def test_fragments_case_and_repeat_download(self):
  for split in range(len('Refresh disk Y/N')+1):
   h=Harness();h.click();h.active();p='Refresh disk Y/N';h.receive(p[:split]);h.receive(p[split:]);h.complete();self.assertEqual(h.writes,[b'Y'])
  h=Harness()
  for _ in range(2):
   self.assertEqual(h.click(),h.base+0x1a14fa);h.active();h.receive('REFRESH\r\n DISK Y / N');h.complete()
  self.assertEqual(h.writes,[b'Y',b'Y'])
 def test_new_request_does_not_complete_old_partial_prompt(self):
  h=Harness();h.receive('Refresh disk Y/');h.click();h.active();h.receive('N');h.complete();self.assertEqual(h.writes,[])
 def test_original_normal_paths(self):
  h=Harness();h.click();h.active();h.receive('N0001 1.2 3.4\r\nEnd of data.')
  for result,expected in [(2,0x1a1574),(1,0x1a1586)]:self.assertEqual(h.run(0x1a156f,[0x1a1574,0x1a1586],eax=result),h.base+expected)
  self.assertEqual(h.writes,[])

class LoggerTextTests(unittest.TestCase):
 def line(self,h,text):
  data=text.encode();ptr=h.INPUT+0x400
  h.put32(ptr-4,len(data));h.uc.mem_write(ptr,data+b'\0');h.put32(h.DIALOG+0xa70,ptr)
  return h.run(MANIFEST['section_rva']+SYMBOLS['line_hook'],[0x14e710],eax=h.DIALOG)
 def test_both_loggers_skip_refresh_prose_but_preserve_handshake(self):
  for base in (0x400000,0x1400000):
   for banner in ('OSU107 Instrument logger SN107, Ver: 0.9.9Q','SAIV110 Surface logger SN107, Ver: 0.9.9Q'):
    h=Harness(base);h.receive(banner+'\r\n');self.assertEqual(h.state('logger_known'),1)
    h.click();h.active()
    self.assertEqual(self.line(h,'Instrument menu is active'),base+0x14e710)
    text='Data logged by the '+banner.split(' SN')[0]+' is stored on its internal disk.'
    h.receive(text+'\r\n');self.assertEqual(self.line(h,text),h.RETURN)
    for text in ('When the device is connected to a PC,','Stop logging before refreshing the disk. Refreshing is blocked while logging is active.','After the refresh, the disk should reappear in File Explorer.'):
     h.receive(text+'\r\n');self.assertEqual(self.line(h,text),h.RETURN)
    h.receive('Refresh disk Y/N');h.complete();self.assertEqual(h.writes,[b'Y'])
 def test_exact_reported_line_and_unknown_instrument(self):
  text='Stop logging before refreshing the disk. Refreshing is blocked while logging is active.'
  h=Harness();h.click();h.active();self.assertEqual(self.line(h,text),h.base+0x14e710)
  h.receive('SAIV110 Surface logger SN107\r\n');self.assertEqual(self.line(h,text),h.RETURN)
 def test_known_logger_log_and_idle_are_not_filtered(self):
  h=Harness();h.receive('OSU107 Instrument logger SN107\r\n')
  self.assertEqual(self.line(h,'Data logged by the OSU107 Instrument Logger'),h.base+0x14e710)
  h.click(log=True);h.active(log=True)
  self.assertEqual(self.line(h,'Data logged by the OSU107 Instrument Logger'),h.base+0x14e710)
 def test_main_port_reconnect_resets_identity(self):
  h=Harness();h.receive('SAIV110 Surface logger SN107\r\n');self.assertEqual(h.state('logger_known'),1)
  h.run(0x7f9c4,[0x7f9c9],eax=h.AUX);self.assertEqual(h.state('logger_known'),1)
  h.run(0x7f9c4,[0x7f9c9],eax=h.COMM);self.assertEqual(h.state('logger_known'),0)
 def test_metadata_and_resource_integrity(self):
  import ast,re
  b=(ROOT/'analysis/single136/SAIV_IT_Runtime.exe').read_bytes();p=pefile.PE(data=b)
  self.assertTrue(p.verify_checksum())
  tree=ast.parse((WORK/'remove_phone_buttons.py').read_text());scope={'struct':struct}
  exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'dfm','exec'),scope)
  for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
   if k.id!=10:continue
   for n in k.directory.entries:
    for l in n.directory.entries:
     r=l.data.struct;blob=p.get_data(r.OffsetToData,r.Size)
     if blob.startswith(b'TPF0'):scope['DfmReader'](blob).parse()

class ReplyTests(unittest.TestCase):
 ACK='System disk refresh will start in 3 seconds. Select the COM port again after reconnect.'
 ERR='ERR: stop surface-logger and wait for the current sample to finish\r\nbefore USB refresh.\r\nRefresh disk Y/N'
 def arm(self,base=0x400000):
  h=Harness(base);h.auto_ack=False
  native=json.loads((WORK/'native136_manifest.json').read_text());h.byte(base+native['rva']+native['symbols']['confirmed_type'],1);h.byte(base+native['rva']+native['symbols']['confirmed_port'],7);h.byte(h.COMM+0x34,7)
  h.click();h.active();h.receive('Refresh disk Y/N')
  rva=MANIFEST['section_rva']+SYMBOLS['wait_for_reply']
  h.run(0x1a156f,[rva],eax=2)
  self.assertEqual(h.writes,[b'Y']);self.assertEqual(h.state('awaiting_reply'),1)
  return h,rva,h.uc.context_save(),bytes(h.uc.mem_read(0x20000000,0x10000))
 def finish(self,h,rva,context,stack):
  h.uc.mem_write(0x20000000,stack);h.uc.context_restore(context)
  h.stops={h.base+0x1a15c7};h.stopped=None
  h.uc.emu_start(h.base+rva,0,count=100000)
  self.assertEqual(h.stopped,h.base+0x1a15c7);self.assertEqual(h.state('awaiting_reply'),0)
 def test_actual_success_response(self):
  for base in (0x400000,0x1400000):
   h,r,ctx,stack=self.arm(base)
   h.receive(self.ACK[:23]);self.assertEqual(h.state('reply_status'),0)
   h.receive(self.ACK[23:]);self.assertEqual(h.state('reply_status'),1)
   self.finish(h,r,ctx,stack)
   self.assertEqual(h.messages,['Performing refresh of disks']);self.assertEqual(h.timeouts,[3000]);self.assertEqual(h.writes,[b'Y'])
 def test_actual_blocked_response(self):
  for base in (0x400000,0x1400000):
   h,r,ctx,stack=self.arm(base);h.receive(self.ERR)
   self.assertEqual(h.state('reply_status'),2);self.finish(h,r,ctx,stack)
   self.assertIn('Stop logging',h.messages[0]);self.assertIn('current sample',h.messages[0]);self.assertEqual(h.timeouts,[]);self.assertEqual(h.writes,[b'Y'])
 def test_timeout_and_unknown_are_not_success(self):
  for response in ('','ERR: another failure','Refresh disk Y/N'):
   h,r,ctx,stack=self.arm();h.receive(response);self.finish(h,r,ctx,stack)
   self.assertEqual(h.sleep_count,250);self.assertIn('was not confirmed',h.messages[0]);self.assertEqual(h.timeouts,[]);self.assertEqual(h.writes,[b'Y'])
 def test_unsolicited_success_is_not_reused(self):
  h=Harness();h.receive(self.ACK);self.assertEqual(h.state('reply_status'),0)
 def test_download_reentry_is_ignored_while_waiting(self):
  h,r,ctx,stack=self.arm();self.assertEqual(h.click(),h.RETURN)
  h.receive(self.ERR);self.finish(h,r,ctx,stack);self.assertEqual(h.writes,[b'Y'])
if __name__=='__main__':unittest.main(verbosity=2)
