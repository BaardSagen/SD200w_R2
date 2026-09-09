"""Compare archived pre-revision conversion formulas with current Delphi machine code; no EXE changes."""
from pathlib import Path
import math,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
src=(ROOT/'analysis/test_recovered_formulas.py').read_text().split('rows=[]')[0]
src=src.replace("SD200W_SAIV_OSU107_NoHandshake.exe","SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe")
src=src.replace('u.emu_start(va,ret+6,count=100000)',"u.mem_write(0x5c60fe,b'\\x01');u.mem_write(0x5b3b6d,b'\\x00');u.emu_start(va,ret+6,count=100000)")
exec(compile(src,'legacy_harness','exec'))
def doc_salinity(C,T):
 C=max(0,C)
 if C<.05:return 0
 r=C/42.914;u=math.sqrt(r);dt=T-15
 return max(0,.008-.1692*u+25.3851*r+14.0941*r*u-7.0261*r*r+2.7081*r*r*u+dt/(1+.0162*dt)*(.0005-.0056*u-.0066*r-.0375*r*u+.0636*r*r-.0144*r*r*u))
def doc_oxygen_ml(S,T):
 k=T+273.15;q=k/100
 return math.exp(-173.4292+249.6339*(100/k)+143.3483*math.log(q)-21.8492*q+S*(-.033096+.014259*q-.0017*q*q))
def doc_sound(S,T,d):
 return 1448.96+4.591*T-.05304*T*T+.0002374*T**3+1.340*(S-35)+.0163*d+1.675e-7*d*d-.01025*T*(S-35)-7.139e-13*T*d**3
rows=[]
for C,T,P in [(42.914,15,0),(42.914,10,0),(30,10,100),(.02,20,0)]:
 rows.append(dict(quantity='salinity',input=dict(C=C,T=T,P=P),document=doc_salinity(C,T),exe=binary(0x50a5b8,[P,C,T])))
rows.append(dict(quantity='sound_m_s',input=dict(T=10,S=35,P=0,D=0),document=doc_sound(35,10,0),exe=binary(0x50a8f0,[0,10,35])))
for air in [760,700]:
 rows.append(dict(quantity='oxygen_mg_L_at_100_percent',input=dict(T=10,S=35,air_mmHg=air),document=doc_oxygen_ml(35,10)*1.42903,exe=binary(0x50bc10,[0,air,10,35])))
old=pefile.PE(str(ROOT/'SD200W_SAIV_OSU107_NoHandshake.exe'))
assert p.get_data(0x10a000,0x3000)==old.get_data(0x10a000,0x3000),'Previously mapped formula region changed'
result=dict(compared_document_archive='analysis/reference/konverteringer_og_eksport_before_SIT_20260908.md',compared_document_sha256='9452c179b1b899f1418e572955d9aa044c10aace1c83134302f87260cc6f487c',document_values_are_pre_revision=True,exe='SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe',sha256=hashlib.sha256((ROOT/'SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe').read_bytes()).hexdigest(),legacy_formula_region_unchanged=True,comparisons=rows,scope='Actual formula calls in x86 emulator; not full import/export UI validation')
(ROOT/'analysis/conversion_document_comparison.json').write_text(json.dumps(result,indent=2))
for row in rows:print(row)
