from pathlib import Path
import pefile,subprocess,hashlib,struct,json
ROOT=Path(__file__).resolve().parent.parent;W=ROOT/'analysis'
source=ROOT/'SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe';out=ROOT/'SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe'
original=source.read_bytes();expected='4b7c492d8fa64b9bf2ffd939ef629d2d82cde7243d766aecb757810e27056b53';assert hashlib.sha256(original).hexdigest()==expected
p=pefile.PE(data=original);b=bytearray(original);rva=p.OPTIONAL_HEADER.SizeOfImage;assert rva==0x298000
native=json.loads((W/'native_uart_detect_manifest.json').read_text());assert native['sha256']==expected and native['rva']==0x297000
classifier=native['symbols']['classify']+native['rva']
subprocess.run(['as','--32','--defsym',f'CLASSIFY={classifier}','-o',str(W/'sd200_selection_g.o'),str(W/'sd200_selection_g.s')],check=True)
assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(W/'sd200_selection_g.o')],text=True)
subprocess.run(['objcopy','-O','binary','-j','.text',str(W/'sd200_selection_g.o'),str(W/'sd200_selection_g.bin')],check=True)
payload=(W/'sd200_selection_g.bin').read_bytes();symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(W/'sd200_selection_g.o')],text=True).splitlines() if len(t:=line.split())==3}
allowed=set()
def put(off,data):b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
def patch(va,old,new):off=p.get_offset_from_rva(va-0x400000);assert b[off:off+len(old)]==old,(hex(va),b[off:off+len(old)].hex());put(off,new)
patch(0x5162c7,bytes.fromhex('ff92d8000000'),b'\xe8'+struct.pack('<i',0x400000+rva-0x5162cc)+b'\x90')
patch(0x51191c,bytes.fromhex('558bec6a00'),b'\xe9'+struct.pack('<i',0x400000+rva+symbols['capture_close']-0x511921))
patch(0x516487,bytes.fromhex('e86c84f6ff'),b'\xe8'+struct.pack('<i',0x400000+rva+symbols['reopen']-0x51648c))
for block in p.DIRECTORY_ENTRY_BASERELOC:
 for e in block.entries:
  assert not (e.type and any(a<=e.rva<a+n for a,n in [(0x1162c7,6),(0x116487,5),(0x11191c,5)]))
entries=[(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
for kind,name,e in entries:
 if (kind==10 and name=='TABOUTBOXNAV') or kind==16:
  data=bytearray(p.get_data(e.OffsetToData,e.Size));old=('1.0.6 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');new=('1.0.7 Sept.2026').encode('utf-16le' if kind==16 else 'ascii');assert old in data;data=data.replace(old,new)
  if kind==16:
   start=data.index(struct.pack('<I',0xfeef04bd));struct.pack_into('<IIII',data,start+8,0x10000,0x70000,0x10000,0x70000)
  put(p.get_offset_from_rva(e.OffsetToData),data)
def align(n,a):return (n+a-1)//a*a
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
put(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
put(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
put(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
assert all(x==b[i] or i in allowed for i,x in enumerate(original))
out.write_bytes(b);assert pefile.PE(str(out)).verify_checksum();assert source.read_bytes()==original
manifest=dict(source=source.name,source_sha256=expected,output=out.name,sha256=hashlib.sha256(b).hexdigest(),rva=rva,symbols=symbols,settle_ms=1100,validation='Pending emulator and GUI tests')
(W/'sd200_selection_g_manifest.json').write_text(json.dumps(manifest,indent=2));print(out.name,manifest['sha256'])
