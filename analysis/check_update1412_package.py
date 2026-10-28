"""Run the unchanged production installer against an inert, owned host.

Reproduce the old case mismatch, then verify the corrected ZIP reaches the
close/install boundary with the exact shipped candidate and version. The host
does not close: the test stops the helper before replacement or SIT startup.
All files remain in the workspace; no AppData extraction or device access.
"""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import hashlib,json,shutil,subprocess,time,zipfile
from check_startup_windows import k,u,SI,PI,CB
R=Path(__file__).resolve().parent.parent
folder=R/'analysis/runtime_test/update1412_package'/str(time.time_ns());folder.mkdir(parents=True)
target=folder/'Field station.exe';shutil.copyfile(R/'analysis/update1412_package_host.exe',target)
old=target.read_bytes();oldhash=hashlib.sha256(old).hexdigest()
manifest=json.loads((R/'update_server/latest.json').read_text())
archive=R/'update_server'/manifest['url'].rsplit('/',1)[1]
entry=archive.with_suffix('.exe').name
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['sha256']
helper=R/'analysis/single1412_hw330/SIT_Update.exe'
build=json.loads((R/'analysis/single_exe_1412_manifest.json').read_text())
assert hashlib.sha256(helper.read_bytes()).hexdigest()==build['helper_sha256']
expected=(R/build['output']).read_bytes()
bad=folder/'old_case_mismatch.zip'
with zipfile.ZipFile(archive) as source,zipfile.ZipFile(bad,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name in source.namelist():z.writestr(build['output'] if name==entry else name,source.read(name))
desktop='SIT_package_'+str(time.time_ns());desk=u.CreateDesktopW(desktop,None,None,0,0x1ff,None);assert desk
si=SI();si.cb=c.sizeof(si);si.desktop=desktop;si.flags=1;si.show=1
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=c.c_ssize_t
host=PI();running=[]
def text(h,cls=False):
 b=c.create_unicode_buffer(4096);(u.GetClassNameW if cls else u.GetWindowTextW)(h,b,len(b));return b.value
def windows(pid):
 rows=[]
 @CB
 def cb(h,l):
  owner=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(owner))
  if owner.value==pid and u.IsWindowVisible(h):rows.append((h,text(h),text(h,True)))
  return True
 u.EnumDesktopWindows(desk,cb,0);return rows
def wait(fn,seconds=15):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  result=fn()
  if result:return result
  time.sleep(.03)
 raise AssertionError('Installer test timed out')
def launch(package):
 args=[str(helper),str(target),str(package),hashlib.sha256(package.read_bytes()).hexdigest(),manifest['version'],entry,oldhash,str(host.pid),str(host.pid),str(main)]
 cmd=c.create_unicode_buffer(subprocess.list2cmdline(args));pi=PI()
 assert k.CreateProcessW(str(helper),cmd,None,None,False,0,None,str(folder),c.byref(si),c.byref(pi))
 running.append(pi);return pi
try:
 assert k.CreateProcessW(str(target),None,None,None,False,0,None,str(folder),c.byref(si),c.byref(host))
 main=wait(lambda:next((h for h,t,cl in windows(host.pid) if cl=='SITPackageTestHost'),None))
 failed=launch(bad)
 box=wait(lambda:next((h for h,t,cl in windows(failed.pid) if cl=='#32770'),None))
 body=[]
 @CB
 def collect(h,l):body.append(text(h));return True
 u.EnumChildWindows(box,collect,0)
 assert 'The ZIP does not contain the expected program' in ' '.join(body),body
 # The expected error dialog belongs to this test helper; end only that process.
 assert k.TerminateProcess(failed.process,0);assert k.WaitForSingleObject(failed.process,5000)==0
 assert target.read_bytes()==old
 installed=launch(archive)
 wait(lambda:text(main)=='SIT installer preflight verified')
 candidates=list(folder.glob('Field station.exe.sit-new-*.exe'));assert len(candidates)==1
 assert candidates[0].read_bytes()==expected
 assert target.read_bytes()==old and not list(folder.glob('*.bak'))
 report=dict(passed=True,version=manifest['version'],manifest_sha256=manifest['sha256'],
  updater_expected_entry=entry,actual_helper_sha256=build['helper_sha256'],
  old_case_mismatch_reproduced=True,corrected_zip_extracted=True,
  candidate_byte_identical=True,embedded_version_accepted=True,
  installer_reached_close_boundary=True,original_host_unchanged=True,
  replacement_and_restart_not_performed=True,no_device_access=True)
 (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 validation=R/'analysis/update_server1412_validation.json';v=json.loads(validation.read_text())
 v['installer_preflight_passed']=True;v['installer_preflight_report']=(folder/'report.json').relative_to(R).as_posix()
 validation.write_text(json.dumps(v,indent=2)+'\n')
 print(json.dumps(report,indent=2))
finally:
 for pi in running+[host]:
  if pi.process:
   k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000)
   k.CloseHandle(pi.thread);k.CloseHandle(pi.process)
 u.CloseDesktop(desk)
 # Only our prepared candidate files, in this unique test folder, are removed.
 for path in folder.glob('Field station.exe.sit-new-*.exe'):path.unlink()
