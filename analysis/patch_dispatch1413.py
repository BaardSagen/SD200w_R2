"""Keep tagged settings/Merge actions out of the batch Convert dispatcher."""
import hashlib,json,struct
from pathlib import Path
import pefile

def patch_dispatch(data,root,work):
    p=pefile.PE(data=bytes(data));b=bytearray(data);entry=0x1a593c
    current=p.get_data(entry,5);assert current[0]==0xe9
    batch=entry+5+struct.unpack('<i',current[1:])[0]
    baseline=(root/'analysis/single1411/SAIV_IT_Runtime.exe').read_bytes()
    assert hashlib.sha256(baseline).hexdigest()=='cd379866e627015607288414a95b68c300183526d850511ffb063b214c72b617'
    prior=pefile.PE(data=baseline).get_data(entry,5);assert prior[0]==0xe9
    legacy=entry+5+struct.unpack('<i',prior[1:])[0]
    # Existing pre-batch dispatch code must be preserved exactly.
    assert p.get_data(legacy,32)==pefile.PE(data=baseline).get_data(legacy,32)
    last=p.sections[-1];align=lambda n,a:(n+a-1)//a*a
    rva=align(last.VirtualAddress+max(last.Misc_VirtualSize,last.SizeOfRawData),16)
    # EAX=self and EDX=sender are Delphi register arguments. Do not modify them.
    # Null sender or Tag=0: existing Convert. Every tagged action: legacy chain.
    code=bytearray(bytes.fromhex('85d2740b837a0c007405e9'))
    code+=struct.pack('<i',legacy-(rva+15))
    code+=b'\xe9'+struct.pack('<i',batch-(rva+20))
    assert len(code)==20
    raw=last.PointerToRawData+rva-last.VirtualAddress;assert raw>=len(b)
    b.extend(bytes(raw-len(b))+code)
    size=align(len(b)-last.PointerToRawData,p.OPTIONAL_HEADER.FileAlignment)
    b.extend(bytes(last.PointerToRawData+size-len(b)))
    for off,value in [(last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(code)),(last.get_field_absolute_offset('SizeOfRawData'),size),(p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(code),p.OPTIONAL_HEADER.SectionAlignment))]:struct.pack_into('<I',b,off,value)
    off=p.get_offset_from_rva(entry);b[off:off+5]=b'\xe9'+struct.pack('<i',rva-entry-5)
    report=dict(entry_rva=entry,dispatcher_rva=rva,batch_rva=batch,legacy_rva=legacy,
                code_hex=code.hex(),convert_tag=0,settings_tags=[0x53495449,0x53495454],merge_tag=0x534d4752)
    (work/'dispatch_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return b
