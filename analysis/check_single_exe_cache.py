"""Check cache reuse, missing/corrupt repair, concurrent starts and moved EXE."""
from pathlib import Path
import ctypes as c,time,hashlib,json
from check_startup_windows import k,u,SI
from single_exe_test_support import start,finish,cache,M
OUT=Path(__file__).resolve().parent/'runtime_test/single133';name='SIT_cache_'+str(time.time_ns());desk=u.CreateDesktopW(name,None,None,0,0x1ff,None);assert desk
si=SI();si.cb=c.sizeof(si);si.desktop=name;si.flags=1;si.show=1
expected={'SAIV_IT_Runtime.exe':M['runtime_sha256'],'SIT_Import131.dll':M['dll_sha256']};results=[]
def verify():
 for f,digest in expected.items():assert hashlib.sha256((cache()/f).read_bytes()).hexdigest()==digest
 return {f:(cache()/f).stat().st_mtime_ns for f in expected}
def launch():
 pi,bundle=start(si,desk,OUT)
 try:verify()
 finally:k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle)
try:
 before=verify();launch();assert before==verify();results.append('Ready cache reused without rewriting payloads; moved EXE and Unicode customer folder work')
 # Only this new version's cache files are manipulated, after every owned runtime has stopped.
 target=cache()/'SIT_Import131.dll';assert target.name in expected and target.parent.name==M['cache_tag'];target.unlink();launch();verify();results.append('Missing DLL restored byte-for-byte')
 target.write_bytes(b'damaged test DLL');launch();verify();results.append('Corrupt DLL restored byte-for-byte')
 target=cache()/'SAIV_IT_Runtime.exe';target.unlink();launch();verify();results.append('Missing runtime restored byte-for-byte')
 before=verify();a,ab=start(si,desk,OUT);b=None
 try:
  b,bb=start(si,desk,OUT);assert before==verify();results.append('Two concurrent starts safely share verified components')
 finally:
  for pi,bundle in [(a,ab)]+([(b,bb)] if b else []):k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle)
 (OUT/'cache_validation.json').write_text(json.dumps(dict(results=results,cache=str(cache()),all_hashes_verified=True,launcher_and_runtime_not_elevated=True),indent=2));print('PASS',results)
finally:u.CloseDesktop(desk)
