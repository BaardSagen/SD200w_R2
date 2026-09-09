import ctypes as c
from ctypes import wintypes as w
from PIL import Image
def capture(hwnd,path,flags=0):
 u=c.WinDLL('user32');g=c.WinDLL('gdi32')
 u.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)]
 u.GetDC.argtypes=[w.HWND];u.GetDC.restype=w.HDC
 u.ReleaseDC.argtypes=[w.HWND,w.HDC]
 u.PrintWindow.argtypes=[w.HWND,w.HDC,w.UINT]
 g.CreateCompatibleDC.argtypes=[w.HDC];g.CreateCompatibleDC.restype=w.HDC
 g.CreateCompatibleBitmap.argtypes=[w.HDC,c.c_int,c.c_int];g.CreateCompatibleBitmap.restype=w.HBITMAP
 g.SelectObject.argtypes=[w.HDC,w.HANDLE];g.SelectObject.restype=w.HANDLE
 g.GetDIBits.argtypes=[w.HDC,w.HBITMAP,w.UINT,w.UINT,c.c_void_p,c.c_void_p,w.UINT]
 g.DeleteObject.argtypes=[w.HANDLE];g.DeleteDC.argtypes=[w.HDC]
 class BI(c.Structure):
  _fields_=[('size',w.DWORD),('width',w.LONG),('height',w.LONG),('planes',w.WORD),('bits',w.WORD),('compression',w.DWORD),('imagesize',w.DWORD),('x',w.LONG),('y',w.LONG),('used',w.DWORD),('important',w.DWORD)]
 rect=w.RECT();assert u.GetWindowRect(hwnd,c.byref(rect))
 width=rect.right-rect.left;height=rect.bottom-rect.top
 dc=u.GetDC(hwnd);mem=g.CreateCompatibleDC(dc);bmp=g.CreateCompatibleBitmap(dc,width,height);old=g.SelectObject(mem,bmp)
 try:
  assert u.PrintWindow(hwnd,mem,flags)
  g.SelectObject(mem,old)
  info=BI();info.size=c.sizeof(BI);info.width=width;info.height=-height;info.planes=1;info.bits=32
  pixels=c.create_string_buffer(width*height*4)
  assert g.GetDIBits(mem,bmp,0,height,pixels,c.byref(info),0)
  Image.frombuffer('RGB',(width,height),pixels.raw,'raw','BGRX',0,1).save(path)
 finally:g.DeleteObject(bmp);g.DeleteDC(mem);u.ReleaseDC(hwnd,dc)
