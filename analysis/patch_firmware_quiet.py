"""Receive gate: capture protocol bytes but skip terminal rendering during firmware jobs."""
import struct, pefile

def patch_firmware_quiet(data):
    p=pefile.PE(data=bytes(data)); b=bytearray(data)
    at=0x19b308; old=p.get_data(at,5)
    assert old==bytes.fromhex('e9 1a 2d 16 00')
    # Existing settings receiver captures each byte through dispatch operation 32.
    assert p.get_data(0x2fe027,19)==bytes.fromhex('9c 60 51 52 0f b6 4c 10 ff 51 6a 20 e8 25 30 ff ff 61 9d')
    # Original per-byte loop continuation, after terminal/echo processing.
    assert p.get_data(0x19b863,10)==bytes.fromhex('ff 45 f8 4e 0f 85 95 fa ff ff')
    rva=p.OPTIONAL_HEADER.SizeOfImage
    code=bytearray(bytes.fromhex('9c 60 51 52 0f b6 4c 10 ff 51 6a 20'))
    def rel(op,target):
        code.append(op);code.extend(struct.pack('<i',target-(rva+len(code)+4)))
    rel(0xe8,0x2f105d) # unchanged native DLL dispatch, stdcall
    code.extend(bytes.fromhex('85 c0 74 07 61 9d'))
    rel(0xe9,0x19b863) # quiet: do not append menu/control bytes to the terminal
    code.extend(bytes.fromhex('61 9d'))
    rel(0xe9,0x299066) # ordinary terminal: preserve original receive processing
    last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress
    assert raw>=len(b)
    align=lambda n,a:(n+a-1)//a*a
    size=align(len(code),p.OPTIONAL_HEADER.FileAlignment)
    struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+len(code))
    struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size)
    struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(code),p.OPTIONAL_HEADER.SectionAlignment))
    b.extend(bytes(raw-len(b))+code+bytes(size-len(code)))
    off=p.get_offset_from_rva(at);b[off:off+5]=b'\xe9'+struct.pack('<i',rva-at-5)
    return b
