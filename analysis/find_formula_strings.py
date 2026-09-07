from pathlib import Path
import re,pefile
p=pefile.PE('SD200W_SAIV_OSU107_NoHandshake.exe');b=Path('SD200W_SAIV_OSU107_NoHandshake.exe').read_bytes()
rows=[]
for m in re.finditer(rb'[\x20-\x7e]{5,}',b):
 s=m.group().decode()
 if re.search(r'salin|densit|sound|oxygen|formula|calc|UNESCO|conduct|polynom|coefficient|sigma|depth|pressure|salinit|potent|weiss|chen|millero',s,re.I):
  try:a=hex(0x400000+p.get_rva_from_offset(m.start()))
  except:a=hex(m.start())
  rows.append(a+' '+s)
Path('analysis/formula_strings.txt').write_text('\n'.join(rows));print('\n'.join(rows))
