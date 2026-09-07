from pathlib import Path
import re,pefile
p=pefile.PE('SD200W_SAIV_OSU107_NoHandshake.exe');b=p.__data__
r=[]
for m in re.finditer(rb'[\x20-\x7e]{5,}',b):
 s=m.group().decode();va=0x400000+p.get_rva_from_offset(m.start())
 if (0x5fd000<va<0x606000 or 0x614c00<va<0x615000 or 0x50a000<va<0x50e000 or 0x53cb00<va<0x53dc00) and (len(s)>12 or '=' in s):r.append(hex(va)+' '+s)
Path('analysis/formula_resource_evidence.txt').write_text('\n'.join(r));print('\n'.join(r))
