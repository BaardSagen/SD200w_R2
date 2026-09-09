"""Hash-chain native changes for separate import and detected-logger Download."""
from pathlib import Path
import ast, json, struct, subprocess, pefile
R=Path(__file__).resolve().parent.parent
def patch_native(data):
    p=pefile.PE(data=bytes(data)); b=bytearray(data); rva=p.OPTIONAL_HEADER.SizeOfImage
    w=R/'analysis/single136'; w.mkdir(exist_ok=True)
    def target(at,opcode):
        code=p.get_data(at,5); assert code[0]==opcode,(hex(at),code.hex())
        return at+5+struct.unpack_from('<i',code,1)[0]
    refresh=json.loads((R/'analysis/refresh_reply_manifest.json').read_text())
    native=json.loads((R/'analysis/native_uart_detect_manifest.json').read_text())
    constants=dict(RVA=rva,OLD_IMPORT_ENTRY=target(0x1a593c,0xe9),OLD_IMPORT_FILE=target(0x1a5a4a,0xe9),
        OLD_CAPTURE=target(0x11191c,0xe9),OLD_SELECTED=target(0x1162c7,0xe8),
        OLD_DOWNLOAD=target(0x1a14f4,0xe9),OLD_LINE=target(0x1496aa,0xe8),
        CLASSIFY=native['rva']+native['symbols']['classify'],
        LOGGER_KNOWN=refresh['section_rva']+refresh['symbols']['logger_known'],
        REQUESTED=refresh['section_rva']+refresh['symbols']['requested'])
    asm='\n'.join('.set %s,%d'%x for x in constants.items())+'\n'+(R/'sit_import/native136.s').read_text()
    (w/'native.s').write_text(asm)
    subprocess.run(['as','--32',str(w/'native.s'),'-o',str(w/'native.o')],check=True)
    assert 'RELOCATION RECORDS' not in subprocess.check_output(['objdump','-r',str(w/'native.o')],text=True)
    subprocess.run(['objcopy','-O','binary','-j','.text',str(w/'native.o'),str(w/'native.bin')],check=True)
    payload=bytearray((w/'native.bin').read_bytes())
    symbols={t[2]:int(t[0],16) for line in subprocess.check_output(['nm','-n',str(w/'native.o')],text=True).splitlines() if len(t:=line.split())==3}
    patches=[]
    def hook(at,label,op=0xe9,length=5):
        off=p.get_offset_from_rva(at); b[off:off+length]=bytes([op])+struct.pack('<i',rva+symbols[label]-at-5)+b'\x90'*(length-5)
        patches.append((at,length))
    for at,label,op,length in [(0x1a593c,'import_entry',0xe9,5),(0x1a5a4a,'import_file',0xe9,5),
        (0x1a5967,'import_title',0xe9,5),(0x1a5993,'import_filter',0xe9,5),
        (0x11191c,'capture',0xe9,5),(0x1162c7,'selected',0xe8,5),
        (0x1a14f4,'download',0xe9,5),(0x1518e4,'prescan',0xe9,8),(0x1496aa,'logger_line',0xe8,5)]:hook(at,label,op,length)
    # The replaced MOV immediate operands were relocated; relative JMPs are not.
    for block in p.DIRECTORY_ENTRY_BASERELOC:
        for e in block.entries:
            if e.type and any(at<=e.rva<at+n for at,n in patches):
                assert e.rva in (0x1a5968,0x1a5994),hex(e.rva)
                struct.pack_into('<H',b,e.struct.get_file_offset(),e.struct.Data&0xfff)
    tree=ast.parse((R/'analysis/remove_phone_buttons.py').read_text(encoding='utf-8-sig'))
    ns={'struct':struct};exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.ClassDef))],type_ignores=[]),'reader','exec'),ns)
    short=lambda s:bytes([len(s)])+s.encode('ascii')
    prop=lambda k,v:short(k)+v
    for k in p.DIRECTORY_ENTRY_RESOURCE.entries:
        for n in k.directory.entries:
            if k.id!=10 or str(n.name)!='TFORM1':continue
            for l in n.directory.entries:
                e=l.data.struct;dfm=p.get_data(e.OffsetToData,e.Size);nodes=ns['DfmReader'](dfm).parse()
                caption=next(t for t in nodes['mnuImportASCII'][1] if t[0]=='Caption')
                _,_,v,z=caption;dfm=dfm[:v]+b'\x06'+short('&Convert CSV/TXT...')+dfm[z:]
                needle=short('TMenuItem')+short('mnuImportASCII');assert dfm.count(needle)==1
                item=short('TMenuItem')+short('mnuImportLegacy')
                item+=prop('Caption',b'\x06'+short('&Import CSV/TXT...'))
                item+=prop('Tag',b'\x04'+struct.pack('<I',0x41534349))
                item+=prop('OnClick',b'\x07'+short('mnuImportASCIIClick'))+b'\0\0'
                at=dfm.index(needle);dfm=dfm[:at]+item+dfm[at:]
                assert set(ns['DfmReader'](dfm).parse())==set(nodes)|{'mnuImportLegacy'}
                payload.extend(bytes((-len(payload))%4));addr=rva+len(payload);payload.extend(dfm)
                struct.pack_into('<II',b,e.get_file_offset(),addr,len(dfm))
    align=lambda n,a:(n+a-1)//a*a
    last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
    size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
    struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(payload))
    struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size)
    struct.pack_into('<I',b,last.get_field_absolute_offset('Characteristics'),last.Characteristics|0xe0000000)
    struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment))
    b.extend(bytes(raw-len(b))+payload+bytes(size-len(payload)))
    q=pefile.PE(data=bytes(b));struct.pack_into('<I',b,q.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),q.generate_checksum())
    (R/'analysis/native136_manifest.json').write_text(json.dumps(dict(rva=rva,symbols=symbols,constants=constants,patches=patches),indent=2))
    return b
