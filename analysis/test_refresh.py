"""Execute refresh hooks with mocked serial writes; no hardware commands."""
from pathlib import Path
import unittest
src=Path(__file__).with_name('test_guard.py').read_text().split('class GuardTests')[0]
src=src.replace("patch_manifest.json","refresh_manifest.json").replace("SD200W_diskguard.exe","SD200W_SAIV_OSU107_Refresh.exe")
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
   self.writes.append(bytes(uc.mem_read(ptr,n)));self.ret()
  elif address==self.RETURN-0x200:
   sp=uc.reg_read(UC_X86_REG_ESP);assert self.cstring(self.get32(sp+4))=='user32.dll'
   uc.reg_write(UC_X86_REG_EAX,123);self.ret(4)
  elif address==self.RETURN-0x300:
   sp=uc.reg_read(UC_X86_REG_ESP);assert self.cstring(self.get32(sp+8))=='MessageBoxTimeoutA'
   uc.reg_write(UC_X86_REG_EAX,self.RETURN-0x400);self.ret(8)
  elif address==self.RETURN-0x400:
   sp=uc.reg_read(UC_X86_REG_ESP)
   self.messages.append(self.cstring(self.get32(sp+8)));self.timeouts.append(self.get32(sp+24));self.ret(24)
  else:super().hook(uc,address,size,unused)
 def complete(self):return self.run(0x1a156f,[0x1a1574,0x1a1586,0x1a15c7],eax=2)
class RefreshTests(unittest.TestCase):
 def test_refresh_once_and_relocated(self):
  for base in (0x400000,0x1400000):
   h=Harness(base);h.click();h.active();h.receive('Data logged by the SAIV110 is stored on its internal disk.\r\nRefresh disk Y/N')
   self.assertEqual(h.writes,[]);self.assertEqual(h.state('pending'),1)
   self.assertEqual(h.complete(),base+0x1a15c7)
   self.assertEqual(h.writes,[b'Y']);self.assertEqual(h.messages,['Preforming refresh off disks']);self.assertEqual(h.timeouts,[3000])
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
if __name__=='__main__':unittest.main(verbosity=2)
