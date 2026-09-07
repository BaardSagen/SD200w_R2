import pefile,struct
p=pefile.PE('SD200W_SAIV_OSU107_NoHandshake.exe');b=p.__data__
for name in (b'CalcBtn3Click',b'CalcBtn1Click',b'CalcBtn5Click',b'CalcBtn7Click',b'Rinkooxygencalibration1Click'):
 start=0
 while True:
  i=b.find(name,start)
  if i<0:break
  start=i+1;va=0x400000+p.get_rva_from_offset(i)
  if va<0x5b0000:print(name.decode(),hex(va),hex(struct.unpack_from('<I',b,i-5)[0]))
