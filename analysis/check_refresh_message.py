import ctypes as c,time,json
from pathlib import Path
u=c.windll.user32
u.CreateDesktopW.argtypes=[c.c_wchar_p,c.c_void_p,c.c_void_p,c.c_uint,c.c_uint,c.c_void_p]
u.CreateDesktopW.restype=c.c_void_p
u.SetThreadDesktop.argtypes=[c.c_void_p]
desktop=u.CreateDesktopW('RefreshTimeoutTest_'+str(time.time_ns()),None,None,0,0x1ff,None)
assert desktop and u.SetThreadDesktop(desktop)
f=c.windll.user32.MessageBoxTimeoutA
f.argtypes=[c.c_void_p,c.c_char_p,c.c_char_p,c.c_uint,c.c_ushort,c.c_uint]
f.restype=c.c_int
start=time.monotonic();result=f(None,b'Preforming refresh off disks',b'MiniSoft SD200W',0x2040,0,3000);elapsed=time.monotonic()-start
assert result in (1,32000),(result,elapsed)
assert 2.8<=elapsed<5,(result,elapsed)
report=dict(result=result,elapsed_seconds=elapsed,passed=True)
Path('analysis/refresh_message_test.json').write_text(json.dumps(report,indent=2));print(report)
