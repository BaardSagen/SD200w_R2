"""Hash-locked About credits and disclaimer update; preserve earlier deliveries."""
from pathlib import Path
import ast, hashlib, json, struct
import pefile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'SD200W_SAIV_v1.0.2_Sept2026.exe'
OUTPUT = ROOT / 'SD200W_SAIV_v1.0.3_Sept2026.exe'
EXPECTED = 'e9f6a7fef0c34537ab32e1d0797d74716e67cd701587de66b3b5a305262424e6'
CREDITS = ('1. Concept and technical specifications: SAIV AS\r\n'
           '2. Original software development: Morten Hammersland Programvare\r\n'
           '3. Further development and maintenance: SAIV AS')
DISCLAIMER = ('Disclaimer:\r\n\r\n'
              'Always keep backup copies of your data files and verify measurement results before relying on them.\r\n\r\n'
              'To the extent permitted by applicable law, neither SAIV AS nor Morten Hammersland Programvare shall be liable for loss of data, loss of profits or indirect damages arising from the use of this software.\r\n\r\n'
              'This notice does not override any applicable contractual obligations or mandatory legal rights.')

# Keep all words and paragraph breaks; shorter lines constrain Delphi MessageDlg.
import textwrap
DISCLAIMER = '\r\n\r\n'.join('\r\n'.join(textwrap.wrap(paragraph, width=48, break_long_words=False, break_on_hyphens=False)) for paragraph in DISCLAIMER.split('\r\n\r\n'))

def build():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == EXPECTED
    p = pefile.PE(data=original)
    tree = ast.parse((ROOT/'analysis/remove_phone_buttons.py').read_text())
    scope = {'struct': struct}
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x, ast.ClassDef) and x.name=='DfmReader'], type_ignores=[]), 'dfm_reader', 'exec'), scope)
    Reader = scope['DfmReader']
    entries = [(k.id,str(n.name),l.data.struct) for k in p.DIRECTORY_ENTRY_RESOURCE.entries for n in k.directory.entries for l in n.directory.entries]
    entry = next(e for k,n,e in entries if k==10 and n=='TABOUTBOXNAV')
    dfm = p.get_data(entry.OffsetToData,entry.Size)
    nodes = Reader(dfm).parse()
    def val(v):
        if isinstance(v,bool): return b'\x09' if v else b'\x08'
        if isinstance(v,int): return b'\x03'+struct.pack('<h',v)
        b=v.encode('latin1')
        return b'\x06'+bytes([len(b)])+b if len(b)<256 else b'\x0c'+struct.pack('<I',len(b))+b
    changes = {
        'AboutBoxNav':dict(ClientWidth=448,ClientHeight=279),
        'Panel1':dict(Width=432,Height=236),
        'Copyright':dict(Left=12,Top=184,Width=408,Height=48,AutoSize=False,WordWrap=False,Caption=CREDITS),
        'Label3':dict(Top=46),
        'Label10':dict(Caption='TD301/TD303/TD304\r\nOSU017 / SurfaceLogger',Top=62,Height=32),
        'LabelVersion':dict(Caption='Version: 1.0.3 Sept.2026',Top=96),
        'BitBtn1':dict(Left=8,Top=248),
        'BitBtn2':dict(Left=168,Top=248),
        'BitBtn3':dict(Left=327,Top=248),
        'Label0':dict(Top=116), 'Label1':dict(Top=116),
        'Label4':dict(Top=132), 'Label9':dict(Top=132),
        'Label5':dict(Top=148), 'Label8':dict(Top=148),
        'Label6':dict(Top=164), 'Label7':dict(Top=164),
    }
    for name in ['ProductName','Label2','Label3','LabelVersion','Label10']:
        changes.setdefault(name,{}).update(Left=80,Width=344)
    edits=[]
    for name,updates in changes.items():
        cls,props,end=nodes[name];found={key:(a,v,z) for key,a,v,z in props};extra=b''
        for key,v in updates.items():
            if key in found:
                a,start,z=found[key];edits.append((start,z,val(v)))
            else:
                keyb=key.encode();extra+=bytes([len(keyb)])+keyb+val(v)
        if extra:edits.append((end,end,extra))
    updated=dfm
    for a,z,v in sorted(edits,reverse=True):updated=updated[:a]+v+updated[z:]
    after=Reader(updated).parse()
    assert nodes.keys()==after.keys()
    for name,(_,props,_) in nodes.items():
        before={key:dfm[v:z] for key,a,v,z in props}
        before.update({key:val(v) for key,v in changes.get(name,{}).items()})
        assert before=={key:updated[v:z] for key,a,v,z in after[name][1]},name
    b=bytearray(original);allowed=set()
    def write(off,data):
        b[off:off+len(data)]=data;allowed.update(range(off,off+len(data)))
    def align(n,a):return (n+a-1)//a*a
    last=p.sections[-1];rva=p.OPTIONAL_HEADER.SizeOfImage
    off=last.PointerToRawData+rva-last.VirtualAddress
    assert off>=len(b)
    payload=bytearray(updated)
    payload.extend(bytes(align(len(payload),4)-len(payload)))
    disclaimer_offset=len(payload)
    text=DISCLAIMER.encode('ascii')
    payload.extend(struct.pack('<iI',-1,len(text))+text+b'\x00')
    disclaimer_va=p.OPTIONAL_HEADER.ImageBase+rva+disclaimer_offset+8
    write(entry.get_field_absolute_offset('OffsetToData'),struct.pack('<I',rva))
    write(entry.get_field_absolute_offset('Size'),struct.pack('<I',len(updated)))
    pointer=p.get_offset_from_rva(0x109e50)
    assert b[pointer-1:pointer+4]==b'\xb8'+struct.pack('<I',0x695d38)
    write(pointer,struct.pack('<I',disclaimer_va))
    # Keep the existing HIGHLOW relocation on the moved string pointer.
    assert any(e.rva==0x109e50 and e.type==3 for block in p.DIRECTORY_ENTRY_BASERELOC for e in block.entries)
    ve=next(e for k,n,e in entries if k==16)
    version=p.get_data(ve.OffsetToData,ve.Size)
    old='1.0.2 Sept.2026'.encode('utf-16le');new='1.0.3 Sept.2026'.encode('utf-16le')
    assert version.count(old)==2
    version=bytearray(version.replace(old,new))
    fixed=version.index(struct.pack('<I',0xfeef04bd))
    struct.pack_into('<IIII',version,fixed+8,0x10000,0x30000,0x10000,0x30000)
    write(p.get_offset_from_rva(ve.OffsetToData),version)
    size=align(len(payload),p.OPTIONAL_HEADER.FileAlignment)
    write(last.get_field_absolute_offset('Misc_VirtualSize'),struct.pack('<I',rva-last.VirtualAddress+len(payload)))
    write(last.get_field_absolute_offset('SizeOfRawData'),struct.pack('<I',rva-last.VirtualAddress+size))
    write(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),struct.pack('<I',align(rva+len(payload),p.OPTIONAL_HEADER.SectionAlignment)))
    b.extend(bytes(off-len(b))+payload+bytes(size-len(payload)))
    write(p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),struct.pack('<I',pefile.PE(data=bytes(b)).generate_checksum()))
    assert all(x==b[i] or i in allowed for i,x in enumerate(original))
    # In executable sections, only the disclaimer pointer and version resource change.
    for section in p.sections:
        if section.Characteristics & 0x20000000:
            a=section.PointerToRawData;z=a+section.SizeOfRawData
            vo=p.get_offset_from_rva(ve.OffsetToData)
            assert all(original[i]==b[i] or pointer<=i<pointer+4 or vo<=i<vo+ve.Size for i in range(a,z))
    check=pefile.PE(data=bytes(b));assert check.verify_checksum()
    assert check.VS_FIXEDFILEINFO[0].FileVersionLS==0x30000
    assert check.get_data(rva+disclaimer_offset+8,len(text))==text
    assert SOURCE.read_bytes()==original
    OUTPUT.write_bytes(b)
    report=dict(source=SOURCE.name,source_sha256=EXPECTED,output=OUTPUT.name,sha256=hashlib.sha256(b).hexdigest(),version='1.0.3 Sept.2026',credits=CREDITS,disclaimer=DISCLAIMER,disclaimer_pointer_rva='0x109e50',disclaimer_va=hex(disclaimer_va),validation='DFM parsed; exact requested text; valid PE checksum and relocation; existing instruction bytes unchanged except disclaimer string address; original preserved.')
    (ROOT/'analysis/compact_about_manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':build()

