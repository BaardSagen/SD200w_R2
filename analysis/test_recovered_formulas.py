from pathlib import Path
import sys,struct,json,math
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
from recovered_formulas import *
p=pefile.PE('SD200W_SAIV_OSU107_NoHandshake.exe')
def binary(va,args,mode=2):
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0,0x1000);u.mem_map(0x400000,0x300000);u.mem_write(0x400000,p.get_memory_mapped_image());u.mem_map(0x20000000,0x20000)
 stack=0x20010000;ret=0x20018000;out=0x20019000
 u.mem_write(ret,b'\xdd\x1d'+struct.pack('<I',out));u.mem_write(stack,struct.pack('<I',ret)+struct.pack('<'+'d'*len(args),*args));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_FPCW,0x37f)
 u.mem_write(0x5b1384,bytes([mode]))
 u.emu_start(va,ret+6,count=100000)
 assert u.reg_read(UC_X86_REG_EIP)==ret+6,hex(u.reg_read(UC_X86_REG_EIP))
 return struct.unpack('<d',u.mem_read(out,8))[0]
rows=[]
for S,T,P in [(35,15,0),(0,0,0),(32,8,100),(35,20,1000),(40,2,4000)]:
 for name,va,args,expected in [('sound_velocity',0x50a8f0,[P,T,S],sound_velocity(S,T,P)),('density_anomaly',0x50c330,[P,T,S],density_anomaly(S,T,P)),('sigma_t',0x50c18c,[T,S],density0(S,T)-1000),('legacy_sigma',0x50bf08,[P,T,S],legacy_sigma(S,T))]:
  actual=binary(va,args,0 if name=='legacy_sigma' else 2);assert math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-8),(name,args,actual,expected)
  rows.append(dict(formula=name,args=args,binary=actual,reconstructed=expected))
for C,T,P in [(42.914,15,0),(0,20,0),(30,10,100),(50,20,1000)]:
 actual=binary(0x50a5b8,[P,C,T]);expected=salinity(C,T,P);assert math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-8),(actual,expected)
 rows.append(dict(formula='salinity',args=[C,T,P],binary=actual,reconstructed=expected))
Path('analysis/formula_numeric_validation.json').write_text(json.dumps(rows,indent=2))
print('PASS',len(rows),'binary versus reconstructed comparisons; no hardware or program changes')
