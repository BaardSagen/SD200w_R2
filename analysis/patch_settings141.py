"""Append instrument settings gates and main-form buttons to preserved 1.3.8."""
from pathlib import Path
import ast,json,struct,subprocess,pefile
R=Path(__file__).resolve().parent.parent

def patch_settings(data):
 p=pefile.PE(data=bytes(data));b=bytearray(data);rva=p.OPTIONAL_HEADER.SizeOfImage;w=R/'analysis/single139';w.mkdir(exist_ok=True)
 prior=json.loads((R/'analysis/native137_manifest.json').read_text());dispatch=prior['rva']+prior['symbols']['dispatch']
 asm='.intel_syntax noprefix\n.code32\n.text\n.global entry\nentry:\n'
 def call(at):return f' .byte 0xe8\n .long {at}-({rva})-(.-entry)-4\n'
 def jump(at):return f' .byte 0xe9\n .long {at}-({rva})-(.-entry)-4\n'
 patches=[]
 for at,label,op,mode in [(0x11191c,'capture',30,'before'),(0x1162c7,'selected',31,'after'),(0x19b308,'receive',32,'byte'),(0x7f9c4,'close',34,'before'),(0x1a593c,'settings',40,'guard'),(0x1a14f4,'download',41,'guard')]:
  old=p.get_data(at,5);assert old[0]==(0xe8 if mode=='after' else 0xe9),(hex(at),old.hex());target=at+5+struct.unpack_from('<i',old,1)[0];patches.append((at,label,old[0],target,op))
  asm+=f'\n.global {label}\n{label}:\n'
  if mode=='after':asm+=call(target)
  asm+=' pushfd\n pushad\n push ecx\n push edx\n'
  if mode=='byte':asm+=' movzx ecx,byte ptr [eax+edx-1]\n push ecx\n'
  else:asm+=' push eax\n'
  asm+=f' push {op}\n'+call(dispatch)
  if mode=='guard':asm+=f' test eax,eax\n jz {label}_old\n popad\n popfd\n ret\n{label}_old:\n'
  asm+=' popad\n popfd\n'+(' ret\n' if mode=='after' else jump(target))
 (w/'settings.s').write_text(asm);subprocess.run(['as','--32',str(w/'settings.s'),'-o',str(w/'settings.o')],check=True);assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(w/'settings.o')],text=True);subprocess.run(['objcopy','-O','binary','-j','.text',str(w/'settings.o'),str(w/'settings.bin')],check=True)
 payload=bytearray((w/'settings.bin').read_bytes());symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(w/'settings.o')],text=True).splitlines() if len(t:=line.split())==3}
 for at,label,opcode,target,op in patches:
  off=p.get_offset_from_rva(at);b[off:off+5]=bytes([opcode])+struct.pack('<i',rva+symbols[label]-at-5)
 t=ast.parse((R/'analysis/remove_phone_buttons.py').read_text(encoding='utf-8-sig'));ns={'struct':struct};exec(compile(ast.Module(body=[next(n for n in t.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'reader','exec'),ns)
 short=lambda s:bytes([len(s)])+s.encode('ascii')
 for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
  for n in k.directory.entries:
   if k.id!=10 or str(n.name)!='TFORM1':continue
   for l in n.directory.entries:
    e=l.data.struct;dfm=p.get_data(e.OffsetToData,e.Size);nodes=ns['DfmReader'](dfm).parse();edits=[]
    for name,top in [('btnPrintEcho',216),('btnCommSetup',328)]:
     key,st,v,z=next(x for x in nodes[name][1] if x[0]=='Top');edits.append((v,z,b'\x03'+struct.pack('<h',top)))
    new=b''
    for name,caption,top,tag,tab in [('btnInterval','&Interval',152,0x53495449,6),('btnTimeDate','TIME/D&ATE',184,0x53495454,7)]:
     new+=short('TButton')+short(name)
     for key,value in [('Left',20),('Top',top),('Width',85),('Height',27),('TabOrder',tab)]:new+=short(key)+b'\x03'+struct.pack('<h',value)
     new+=short('Caption')+b'\x06'+short(caption)+short('Tag')+b'\x04'+struct.pack('<I',tag)+short('OnClick')+b'\x07'+short('mnuImportASCIIClick')+b'\0\0'
    at=nodes['btnDownload'][2]+2;assert dfm[at-2:at]==b'\0\0';edits.append((at,at,new))
    for st,z,value in sorted(edits,reverse=True):dfm=dfm[:st]+value+dfm[z:]
    assert set(ns['DfmReader'](dfm).parse())==set(nodes)|{'btnInterval','btnTimeDate'}
    payload.extend(bytes((-len(payload))%4));addr=rva+len(payload);payload.extend(dfm);struct.pack_into('<II',b,e.get_file_offset(),addr,len(dfm))
 align=lambda n,a:(n+a-1)//a*a;last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b);size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
 struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload));struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment));b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
 q=pefile.PE(data=bytes(b));struct.pack_into('<I',b,q.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),q.generate_checksum());(R/'analysis/settings141_manifest.json').write_text(json.dumps(dict(rva=rva,symbols=symbols,patches=patches,dispatch=dispatch),indent=2));return b
