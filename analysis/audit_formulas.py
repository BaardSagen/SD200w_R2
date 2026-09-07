from pathlib import Path
src=Path('analysis/test_recovered_formulas.py').read_text().split('rows=[]')[0]
src=src.replace('def binary(va,args,mode=2):','def binary(va,args,mode=2,sensor=True):').replace('u.emu_start(va,ret+6,count=100000)',"u.mem_write(0x5c60fe,bytes([int(sensor)]));u.mem_write(0x5b3b6d,b'\\x00')\n u.emu_start(va,ret+6,count=100000)")
exec(compile(src,'harness','exec'))
r=[]
for C,T,P,ref in [(34.5487,28.7856,10,20.009869599086951),(34.7275,28.4329,50,20.26551186487427),(34.8605,22.8103,125,22.981513062527689),(34.6810,10.2600,250,31.204503263727982),(34.5680,6.8863,600,34.032315787432829),(34.5600,4.4036,1000,36.400308494388170)]:
 r.append(dict(test='GSW published reference',C=C,T90=T,P=P,reference=ref,binary_T68=binary(0x50a5b8,[P,C,T*1.00024]),binary_unconverted=binary(0x50a5b8,[P,C,T])))
for C in [-999,-1,0,.00999,.01,.02,.1,1]:
 r.append(dict(test='conductivity boundary',C=C,S=binary(0x50a5b8,[0,C,20])))
for S in [-999,-1,0,35]:
 r.append(dict(test='density with input S',S=S,result=binary(0x50c330,[0,20,S])))
for S in [0,5,35]:
 for sensor in [True,False]:
  try:r.append(dict(test='oxygen wrapper',S=S,sensor=sensor,result=binary(0x50bc10,[0,760,20,S],sensor=sensor)))
  except Exception as e:r.append(dict(test='oxygen wrapper',error=str(e)))
for S,T,P in [(35,15,0),(32,8,100),(40,20,1000)]:
 C=binary(0x50a6e0,[P,S,T]);r.append(dict(test='inverse roundtrip',S=S,T=T,P=P,C=C,recovered=binary(0x50a5b8,[P,C,T])))
Path('analysis/formula_audit_tests.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

