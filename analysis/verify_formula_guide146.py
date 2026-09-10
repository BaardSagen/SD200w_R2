"""Equation checks against preserved SIT runtime; never opens an instrument."""
from pathlib import Path
import sys, struct, json, math, hashlib
R=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(R/'analysis/python_packages'),str(R/'analysis')]
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_FPCW, UC_X86_REG_EIP
from recovered_formulas import *
p=pefile.PE(str(R/'analysis/single145/SAIV_IT_Runtime.exe'))
def machine():
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0,0x1000);u.mem_map(0x400000,0x400000)
 u.mem_write(0x400000,p.get_memory_mapped_image())
 u.mem_map(0x20000000,0x20000);u.reg_write(UC_X86_REG_FPCW,0x37f)
 return u
def run(u,va,args):
 stack=0x20010000;ret=0x20018000;out=0x20019000
 u.mem_write(ret,b'\xdd\x1d'+struct.pack('<I',out))
 u.mem_write(stack,struct.pack('<I',ret)+args);u.reg_write(UC_X86_REG_ESP,stack)
 u.emu_start(va,ret+6,count=100000)
 assert u.reg_read(UC_X86_REG_EIP)==ret+6,hex(u.reg_read(UC_X86_REG_EIP))
 return struct.unpack('<d',u.mem_read(out,8))[0]
def binary(va,args,mode=2):
 u=machine();u.mem_write(0x5b1384,bytes([mode]));u.mem_write(0x5c60fe,b'\x01');u.mem_write(0x5b3b6d,b'\x00')
 return run(u,va,struct.pack('<'+'d'*len(args),*args))
checks=[]
def check(label,actual,expected):
 assert math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-8),(label,actual,expected)
 checks.append(dict(test=label,native=actual,reference=expected))
for S,T,P in [(35,15,0),(0,0,0),(32,8,100),(35,20,1000),(40,2,4000),(32.539,7.773,16.72)]:
 for name,va,args,expected,mode in [('sound',0x50a8f0,[P,T,S],sound_velocity(S,T,P),2),('rho anomaly',0x50c330,[P,T,S],density_anomaly(S,T,P),2),('sigma T',0x50c18c,[T,S],density0(S,T)-1000,2),('legacy density',0x50bf08,[P,T,S],legacy_sigma(S,T),0)]:
  check(name,binary(va,args,mode),expected)
for C,T,P in [(30,10,100),(.05,23,0),(.00999,20,0),(.01,20,0),(42.914,10,0)]:
 check('salinity',binary(0x50a5b8,[P,C,T]),salinity(C,T,P))
for S,T,AP in [(0,20,760),(35,10,700),(32.539,7.773,925*760/1013.25)]:
 check('oxygen normal',binary(0x50bc10,[0,AP,T,S]),oxygen_saturation_mg_l(S,T,AP))
# Literal stores in the checkbox handler, verified from current binary bytes.
assert b'\xc7\x00\xc3\xf5\x28\x5c\xc7\x40\x04\x8f\x12\x71\x40' in p.get_data(0x146009,18)
assert b'\xc7\x00\x66\x66\x66\x66\xc7\x40\x04\x66\x12\x71\x40' in p.get_data(0x14601d,18)
kelvin={'checked':struct.unpack('<d',bytes.fromhex('c3f5285c8f127140'))[0],'unchecked':struct.unpack('<d',bytes.fromhex('6666666666127140'))[0]}
# Exercise both branch bodies and the calibrated temperature routines.
for old,start in [(True,0x546009),(False,0x54601d)]:
 u=machine();u.mem_write(0x5b1cfc,struct.pack('<I',0x20000100));u.emu_start(start,0x54602f,count=20)
 K=struct.unpack('<d',u.mem_read(0x20000100,8))[0];assert K==kelvin['checked' if old else 'unchecked']
 for ccoef in [0,1e-7]:
  a,b,d,Rohm=.0011,.00024,8e-8,10000
  expected=1/(a+b*math.log(Rohm)+ccoef*math.log(Rohm)**2+d*math.log(Rohm)**3)-K
  check('temperature four coefficients',run(u,0x52a320,struct.pack('<5d',d,ccoef,b,a,Rohm)),expected)
  if not ccoef:check('temperature three coefficients',run(u,0x52a2ec,struct.pack('<4d',d,b,a,Rohm)),expected)
# Profile recurrence test: retain native layer and interpolation code, supply
# controlled density/gravity callees. This does NOT validate whole-file dispatch.
u=machine();parent=0x20002000;data=0x20003000;table=0x20004000
u.mem_write(0x5b2150,struct.pack('<I',0x20000200));u.mem_write(0x20000200,struct.pack('<I',data))
u.mem_write(0x5c6f00,struct.pack('<I',table));u.mem_write(0x5c6f04,struct.pack('<I',0))
# Native callees replaced with fld constant; ret <argument bytes>.
u.mem_write(0x50bb94,b'\xdd\x05'+struct.pack('<I',0x20000300)+b'\xc2\x18\x00')
u.mem_write(0x50cc1c,b'\xdd\x05'+struct.pack('<I',0x20000308)+b'\xc2\x08\x00')
z=0;prev=0
for i,(P,rho,g) in enumerate([(1,1005,9.81),(10,1020,9.82),(25,1028,9.83)]):
 u.mem_write(parent-4,struct.pack('<i',i));u.mem_write(data+i*52+0x24,struct.pack('<d',P))
 u.mem_write(0x20000300,struct.pack('<2d',rho-1000,g));z+=10000*(P-prev)/(rho*g);prev=P
 check('native profile layer with controlled rho/g',run(u,0x50d1e0,struct.pack('<I',parent)),z)
knots=[struct.unpack('<2d',u.mem_read(table+i*16,16)) for i in range(3)]
# Delphi dynamic array high bound reads length from pointer-4.
u.mem_write(table-4,struct.pack('<I',3))
for P in [.5,5,20]:
 u.mem_write(parent-4,struct.pack('<i',3));u.mem_write(parent-8,struct.pack('<i',1));u.mem_write(data+3*52+0x24,struct.pack('<d',P))
 if P<knots[0][0]:expected=P*knots[0][1]/knots[0][0]
 else:
  lo,hi=next((knots[i-1],knots[i]) for i in range(1,3) if knots[i-1][0]<=P<=knots[i][0]);expected=lo[1]+(P-lo[0])*(hi[1]-lo[1])/(hi[0]-lo[0])
 check('native profile interpolation',run(u,0x50d024,struct.pack('<I',parent)),expected)
S,T,P,AP,percent=32.539,7.773,16.72,925.,3.47
C=binary(0x50a6e0,[P,S,T]);rho=1000+density_anomaly(S,T,P);g=gravity(45.508368287,P)
check('inverse salinity round trip',binary(0x50a5b8,[P,C,T]),S)
mg=oxygen_saturation_mg_l(S,T,AP*760/1013.25)*percent/100
example=dict(S=S,T=T,P=P,AP_hPa=AP,percent=percent,inverse_C=C,C_rounded6_to_S=salinity(round(C,6),T,P),rho=rho,sigmaT=density0(S,T)-1000,gravity=g,depth=P*10000/(rho*g),unesco=depth_unesco(45.508368287,P),sound=sound_velocity(S,T,P),fahrenheit=T*1.8+32,oxygen100=mg*100/percent,mg_L=mg,mL_L=mg*22.391/31.998,umol_L=mg*1000/31.998,umol_kg=mg*22.391*1000/(716.467218*(rho/1000)),AP_mmHg=AP*760/1013.25)
example['two_layer_depth']=10000*.30/((1000+density_anomaly(23.738,14.461,.30))*gravity(45.508368287,.30))+10000*(P-.30)/(rho*g)
report=dict(runtime_sha256=hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest() if hasattr(p,'__file__') else hashlib.sha256((R/'analysis/single145/SAIV_IT_Runtime.exe').read_bytes()).hexdigest(),kelvin=kelvin,checks=checks,example=example,profile_scope='Native recurrence and interpolation with controlled density/gravity; not whole-file profiling acceptance',instrument_commands=False)
(R/'analysis/formula_guide146_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(passed=len(checks),example=example),indent=2))
