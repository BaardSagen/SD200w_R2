from pathlib import Path
import sys,pefile,struct,json,math
sys.path.insert(0,'analysis/python_packages');sys.path.insert(0,'analysis')
from unicorn import *
from unicorn.x86_const import *
from recovered_formulas import gravity,density_anomaly
p=pefile.PE('SAIV_Instrument_Terminal_v1.2.0_Sept2026.exe')
def binary(va,args,latitude,gps):
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0,0x1000);u.mem_map(0x400000,0x400000);u.mem_write(0x400000,p.get_memory_mapped_image());u.mem_map(0x20000000,0x20000)
 stack=0x20010000;ret=0x20018000;out=0x20019000
 u.mem_write(ret,b'\xdd\x1d'+struct.pack('<I',out));u.mem_write(stack,struct.pack('<I',ret)+struct.pack('<'+'d'*len(args),*args));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_FPCW,0x37f)
 for i,(addr,value) in enumerate([(0x5b1680,2),(0x5b1a6c,1),(0x5b226c,int(gps)),(0x5b1b7c,1),(0x5b1adc,1)]):
  target=0x20012000+16*i;u.mem_write(addr,struct.pack('<I',target));u.mem_write(target,struct.pack('<I',value))
 u.mem_write(0x5b1884,struct.pack('<I',0x20013000));u.mem_write(0x20013014,struct.pack('<d',latitude));u.mem_write(0x5b1384,b'\x02')
 u.emu_start(va,ret+6,count=100000);assert u.reg_read(UC_X86_REG_EIP)==ret+6
 return struct.unpack('<d',u.mem_read(out,8))[0]
rows=[]
for S,T,P,lat,gps in [(35,10,1000,60,True),(0,20,100,0,True),(35,0,4000,-70,True),(10,5,0,45,True),(35,15,-.01,60,True),(35,10,1000,0,False)]:
 used=lat if gps else 45.508368287
 g=binary(0x50cb5c,[used,P],used,gps);assert math.isclose(g,gravity(used,P),rel_tol=1e-12)
 expected=P*10000/((1000+density_anomaly(S,T,P))*g)
 actual=binary(0x50bcf8,[0,P,T,S],lat,gps);assert math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-10),(actual,expected)
 rows.append(dict(S=S,T=T,P=P,latitude=used,gps=gps,native_depth=actual,reference_depth=expected,native_gravity=g))
Path('analysis/native_depth_import_validation.json').write_text(json.dumps(rows,indent=2));print('PASS',len(rows),'native fixed-position depth and gravity cases')
