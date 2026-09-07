import sys,json,ctypes as c
sys.path.insert(0,'analysis');import check_startup_windows as x
x.k.OpenProcess.argtypes=[x.w.DWORD,x.w.BOOL,x.w.DWORD];x.k.OpenProcess.restype=x.w.HANDLE
h=x.k.OpenProcess(0x410,False,28652);assert h
peb=c.c_size_t();assert x.n.NtQueryInformationProcess(h,26,c.byref(peb),c.sizeof(peb),None)==0
def read(a):
 v=x.w.DWORD();assert x.k.ReadProcessMemory(h,a,c.byref(v),4,None);return v.value
base=read(peb.value+8);form=read(base+0x1c8964);comm=read(form+0x510);dlg=read(read(base+0x1b21e0))
print(json.dumps(dict(base=hex(base),form=hex(form),hwnd=read(form+0x14c),serial=read(comm+0x2c),port=read(comm+0x34)&255,flags={hex(i):read(comm+i) for i in [0x24,0x30,0x4c,0x407c,0x4080]},download={hex(i):read(dlg+i) for i in [0xa60,0xa64,0x234]},visible=bool(x.u.IsWindowVisible(read(form+0x14c))))))
