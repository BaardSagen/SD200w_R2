import sys,pefile,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
from capstone import *
p=pefile.PE('SD200W_SAIV_OSU107_NoHandshake.exe');cs=Cs(CS_ARCH_X86,CS_MODE_32)
cs.skipdata=True
a=int(sys.argv[1],16);end=int(sys.argv[2],16)
for i in cs.disasm(p.get_data(a-0x400000,end-a),a):
 s=f'{i.address:08x} {i.mnemonic:8} {i.op_str}'
 import re
 m=re.search(r'\[0x([0-9a-f]+)\]',i.op_str)
 if m and i.mnemonic.startswith('f'):
  addr=int(m[1],16)
  try:
   b=p.get_data(addr-0x400000,10)
   if 'dword ptr' in i.op_str:s+=' ; '+str(struct.unpack('<f',b[:4])[0])
   elif 'xword ptr' in i.op_str:s+=' ; '+str((-1 if b[9]&128 else 1)*int.from_bytes(b[:8],'little')*2.0**((int.from_bytes(b[8:10],'little')&32767)-16383-63))
   elif 'qword ptr' in i.op_str:s+=' ; '+str(struct.unpack('<d',b[:8])[0])
  except:pass
 print(s)


