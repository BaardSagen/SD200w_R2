"""Extend 1.3.6 runtime with selective native-field interoperability hooks."""
from pathlib import Path
import json,struct,subprocess,pefile,sys
sys.path.insert(0,str(Path(__file__).parent/'python_packages'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
R=Path(__file__).resolve().parent.parent

def patch_native(data):
 p=pefile.PE(data=bytes(data));b=bytearray(data);rva=p.OPTIONAL_HEADER.SizeOfImage;w=R/'analysis/single137';w.mkdir(exist_ok=True)
 old=json.loads((R/'analysis/native136_manifest.json').read_text());constants=dict(RVA=rva,ASCII_MODE=old['rva']+old['symbols']['ascii_mode'],OLD_IMPORT_FILE=old['rva']+old['symbols']['import_file'])
 s='\n'.join('.set %s,%d'%x for x in constants.items())+'\n'+(R/'sit_import/native137.s').read_text()
 specs=[(0x1a5a4a,'import_file',None,5),(0x1a0a44,'open_dialog',None,5)]
 # The handler returns 1 only when it fully handles this imported dataset.
 for at,label,op,clean in [(0x190710,'load',2,0),(0x1a100c,'graph',3,0),(0x1a0f98,'depth_graph',17,0),(0x1a38dc,'multi',4,0),(0x1a0f40,'list',5,0),(0x156a98,'fill',6,4),(0x157f04,'readout',8,0),(0x159288,'graph_destroy',10,0),(0x158704,'graph_base',18,0),(0x158d6c,'all_points',19,0),(0x19bee8,'update',20,0),(0x1a0cd4,'menu_time',21,0),(0x1a09ac,'menu_depth',22,0),(0x1a0d14,'menu_depth_time',23,0),(0x1a7ddc,'close_file',11,0)]:
  ins=[];n=0
  for i in Cs(CS_ARCH_X86,CS_MODE_32).disasm(p.get_data(at,32),at):
   assert not i.mnemonic.startswith('j') and (i.mnemonic!='call' or i.bytes[0]==0xe8),(label,i.mnemonic)
   ins.append(i);n+=i.size
   if n>=5:break
  raw=p.get_data(at,n);replay='';
  for i in ins:
   if i.mnemonic=='call':replay+=' .byte 0xe8\n .long '+str(int(i.op_str,16))+'-RVA-(.-entry)-4\n'
   else:replay+=' .byte '+','.join(str(x) for x in i.bytes)+'\n'
  specs.append((at,label,op,n));s+=f'\n.global {label}\n{label}:\n pushfd\n pushad\n push ecx\n push edx\n push eax\n push {op}\n call dispatch\n test eax,eax\n jz {label}_old\n popad\n popfd\n ret {clean}\n{label}_old:\n popad\n popfd\n'+replay+f' jump {at+n}\n'
 (w/'native.s').write_text(s);subprocess.run(['as','--32',str(w/'native.s'),'-o',str(w/'native.o')],check=True);assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(w/'native.o')],text=True);subprocess.run(['objcopy','-O','binary','-j','.text',str(w/'native.o'),str(w/'native.bin')],check=True)
 payload=(w/'native.bin').read_bytes();symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(w/'native.o')],text=True).splitlines() if len(t:=line.split())==3}
 for at,label,op,n in specs:
  off=p.get_offset_from_rva(at);b[off:off+n]=b'\xe9'+struct.pack('<i',rva+symbols[label]-at-5)+b'\x90'*(n-5)
  for block in p.DIRECTORY_ENTRY_BASERELOC:
   for e in block.entries:
    assert not(e.type and at<=e.rva<at+n),(label,hex(e.rva),'relocation in relocated prologue')
 align=lambda n,a:(n+a-1)//a*a;last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
 struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload));struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size);struct.pack_into('<I',b,last.get_field_absolute_offset('Characteristics'),last.Characteristics|0xe0000000);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment));b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
 q=pefile.PE(data=bytes(b));struct.pack_into('<I',b,q.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),q.generate_checksum());(R/'analysis/native137_manifest.json').write_text(json.dumps(dict(rva=rva,symbols=symbols,constants=constants,patches=specs),indent=2));return b
