"""Execute the original and patched history trimming loops with mock TStrings."""
from pathlib import Path
import json, struct, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'analysis'/'python_packages'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *

def check(filename,base,count,limit):
    p=pefile.PE(str(ROOT/filename))
    if base!=p.OPTIONAL_HEADER.ImageBase: p.relocate_image(base)
    u=Uc(UC_ARCH_X86,UC_MODE_32)
    u.mem_map(base,p.OPTIONAL_HEADER.SizeOfImage)
    u.mem_write(base,bytes(p.get_memory_mapped_image()))
    u.mem_map(0x10000000,0x10000)
    form=0x10001000; strings=0x10003000; vmt=0x10004000; frame=0x10006000; stack=0x10008000
    def put(a,v): u.mem_write(a,struct.pack('<I',v))
    put(form+0xc14,strings);put(strings,vmt)
    put(vmt+0x14,0x10005000);put(vmt+0x44,0x10005010);put(vmt+0x34,0x10005020)
    put(frame-4,0x12345678)
    u.reg_write(UC_X86_REG_EBX,form);u.reg_write(UC_X86_REG_EBP,frame);u.reg_write(UC_X86_REG_ESP,stack)
    lines=list(range(count));removed=[];finished=[]
    def ret():
        sp=u.reg_read(UC_X86_REG_ESP)
        target=struct.unpack('<I',u.mem_read(sp,4))[0]
        u.reg_write(UC_X86_REG_ESP,sp+4);u.reg_write(UC_X86_REG_EIP,target)
    def hook(uc,a,size,data):
        if a==base+0x19bcd7:
            finished.append(True);u.emu_stop()
        elif a==0x10005000:
            assert u.reg_read(UC_X86_REG_EAX)==strings
            u.reg_write(UC_X86_REG_EAX,len(lines));ret()
        elif a==0x10005010:
            assert u.reg_read(UC_X86_REG_EDX)==0
            removed.append(lines.pop(0));ret()
        elif a==0x10005020:
            assert u.reg_read(UC_X86_REG_EDX)==0x12345678
            lines.append(count);ret()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(base+0x19bcb0,0,count=200000)
    assert finished
    assert lines==list(range(max(0,count-limit),count+1))
    assert removed==list(range(max(0,count-limit)))
    assert u.reg_read(UC_X86_REG_ESP)==stack
    return dict(base=hex(base),input_lines=count,retained_lines=len(lines),oldest_line=lines[0])

reports=[]
for base in [0x400000,0x1400000]:
    for count in [0,99,100,101,1000,1999,2000,2001,2500,5000]:
        reports.append(check('SD200W_SAIV_OSU107_History.exe',base,count,2000))
baseline=check('SD200W_SAIV_OSU107_Instrument_v2.exe',0x400000,1500,100)
extended=check('SD200W_SAIV_OSU107_History.exe',0x400000,1500,2000)
assert baseline['oldest_line']==1400 and extended['oldest_line']==0
report=dict(result='PASS',boundary_cases=len(reports),baseline=baseline,extended=extended,cases=reports)
(ROOT/'analysis'/'scrollback_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: 20 boundary/rebased execution cases; 1500-line comparison retains all 1500 earlier lines instead of only 100.')
