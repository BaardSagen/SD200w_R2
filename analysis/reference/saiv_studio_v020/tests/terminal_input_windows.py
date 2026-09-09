"""Exercise real WM_CHAR handling with a file-backed test transport, never a COM port."""
from pathlib import Path
import subprocess,ctypes as c,time,json,hashlib
from ctypes import wintypes as w
from PIL import ImageGrab
R=Path(__file__).resolve().parents[1];out=R/'test-results';wire=out/'terminal-input.bin';exe=R/'build/SAIVStudio.exe'
u=c.WinDLL('user32');CB=c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.EnumWindows.argtypes=[CB,w.LPARAM];u.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)];u.IsWindowVisible.argtypes=[w.HWND];u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)];u.ClientToScreen.argtypes=[w.HWND,c.POINTER(w.POINT)];u.SetForegroundWindow.argtypes=[w.HWND]
p=subprocess.Popen([str(exe),'--demo','--terminal-test',str(wire)],cwd=out)
try:
 time.sleep(2);found=[]
 @CB
 def enum(h,l):
  pid=w.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
  if pid.value==p.pid and u.IsWindowVisible(h):found.append(h)
  return True
 u.EnumWindows(enum,0);assert found;h=found[0];u.SetForegroundWindow(h);time.sleep(.4)
 def char(ch):u.PostMessageW(h,0x102,ord(ch),1)
 def click(x,y):
  pt=w.POINT(x,y);u.ClientToScreen(h,c.byref(pt));u.SetCursorPos(pt.x,pt.y);time.sleep(.1);u.mouse_event(2,0,0,0,0);time.sleep(.1);u.mouse_event(4,0,0,0,0);time.sleep(.3)
 r=w.RECT();u.GetWindowRect(h,c.byref(r));ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out/'terminal_debug.png')
 click(700,-15) # Activate title bar; do not focus a text field.
 # Initial terminal owns keyboard without clicking a text field.
 for ch in 'ISm\r\x08\x13\x11':char(ch)
 time.sleep(.9);expected=b'ISm\r\x08\x13\x11';assert wire.read_bytes()==expected,wire.read_bytes()
 r=w.RECT();u.GetWindowRect(h,c.byref(r));ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out/'terminal_0_2.png')
 # Setup is the fourth main action; characters here must not reach transport.
 click(435,60);click(550,380);char('Z');time.sleep(.4);assert wire.read_bytes()==expected,'setup leaked a character'
 ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out/'setup_0_2.png')
 click(525,506);char('Q');time.sleep(.6);expected+=b'Q';assert wire.read_bytes()==expected,'terminal did not regain keyboard after Setup'
 for name,x in [('data',125),('utilities',202),('logger',280),('about',350)]:
  click(x,22);char('X');time.sleep(.4);assert wire.read_bytes()==expected,'non-terminal page sent input'
  ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out/(name+'_0_2.png'))
 click(40,22);char('G');time.sleep(.5);expected+=b'G';assert wire.read_bytes()==expected
 ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out/'terminal_0_2.png')
 u.PostMessageW(h,0x10,0,0);assert p.wait(timeout=10)==0
 (out/'terminal_input_validation.json').write_text(json.dumps(dict(result='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),bytes_sent=expected.hex(),direct_input=True,setup_does_not_send=True,serial_ports_opened=0),indent=2))
 print('PASS direct WM_CHAR input on startup, exact control bytes, no Setup leakage, clean exit')
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=5)
