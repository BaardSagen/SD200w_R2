"""Reproducible, hash-locked patch for the supplied SD200W.exe only."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import pefile

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / 'analysis'
SOURCE = ROOT / 'SD200W.exe'
OUTPUT = ROOT / 'SD200W_diskguard.exe'
EXPECTED_SHA256 = 'c7c08b02f0a63ddf986fac9cd325634dd60421354daf18daa13d01d831728b4e'

def align(value, alignment):
    return (value + alignment - 1) // alignment * alignment

def build():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == EXPECTED_SHA256, 'Unexpected EXE version'
    pe = pefile.PE(data=original)
    assert pe.FILE_HEADER.Machine == 0x14c
    base = pe.OPTIONAL_HEADER.ImageBase
    last = pe.sections[-1]
    rva = align(last.VirtualAddress + last.Misc_VirtualSize, pe.OPTIONAL_HEADER.SectionAlignment)
    assert rva == 0x23d000, 'Assembly image layout mismatch'
    subprocess.run(['as', '--32', '-o', str(WORK/'download_guard.o'), str(WORK/'download_guard.s')], check=True)
    relocations = subprocess.check_output(['objdump', '-r', str(WORK/'download_guard.o')], text=True)
    assert 'RELOCATION RECORDS' not in relocations, 'Payload must be position independent'
    subprocess.run(['objcopy', '-O', 'binary', '-j', '.text', str(WORK/'download_guard.o'), str(WORK/'download_guard.bin')], check=True)
    payload = (WORK/'download_guard.bin').read_bytes()
    symbols = {}
    for line in subprocess.check_output(['nm', '-n', str(WORK/'download_guard.o')], text=True).splitlines():
        parts = line.split()
        if len(parts) == 3:
            symbols[parts[2]] = int(parts[0], 16)
    changes = [
        (0x59b308, '8a5c10ff8bc3', 'receive_hook'),
        (0x5a14f4, '53568bf28bd8', 'click_hook'),
        (0x5a156f, '83f8027512', 'after_modal_hook'),
        (0x47f9c4, '558bec33c9', 'close_port_hook'),
    ]
    result = bytearray(original)
    records = []
    for address, expected_hex, label in changes:
        expected = bytes.fromhex(expected_hex)
        offset = pe.get_offset_from_rva(address-base)
        assert result[offset:offset+len(expected)] == expected
        # These overwritten instructions must not contain base relocation entries.
        for block in pe.DIRECTORY_ENTRY_BASERELOC:
            for entry in block.entries:
                assert not entry.type or not address-base <= entry.rva < address-base+len(expected)
        target = base + rva + symbols[label]
        patched = b'\xe9' + struct.pack('<i', target-address-5) + b'\x90'*(len(expected)-5)
        result[offset:offset+len(expected)] = patched
        records.append(dict(address=hex(address), offset=offset, original=expected_hex, patched=patched.hex(), label=label))
    # Append a separate payload section; preserve every original section and overlay byte.
    raw = align(len(result), pe.OPTIONAL_HEADER.FileAlignment)
    raw_size = align(len(payload), pe.OPTIONAL_HEADER.FileAlignment)
    header = last.get_file_offset()+40
    assert header+40 <= pe.OPTIONAL_HEADER.SizeOfHeaders
    # This signed Delphi image has an unused, unnamed ninth header slot.
    # It has zero virtual/raw size and points at the certificate overlay.
    unused = struct.unpack_from('<8sIIIIIIHHI', result, header)
    assert unused[0] == bytes(8) and unused[1] == 0 and unused[3] == 0
    assert unused[2] == rva and unused[4] == pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].VirtualAddress
    struct.pack_into('<8sIIIIIIHHI', result, header, b'.dlguard', len(payload), rva, raw_size, raw, 0, 0, 0, 0, 0xe0000060)
    struct.pack_into('<H', result, pe.FILE_HEADER.get_field_absolute_offset('NumberOfSections'), len(pe.sections)+1)
    struct.pack_into('<I', result, pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'), align(rva+len(payload), pe.OPTIONAL_HEADER.SectionAlignment))
    struct.pack_into('<I', result, pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'), pe.OPTIONAL_HEADER.SizeOfCode+raw_size)
    # Modification invalidates the original Authenticode signature. Do not advertise it as valid.
    security = pe.OPTIONAL_HEADER.DATA_DIRECTORY[4]
    result[security.get_file_offset():security.get_file_offset()+8] = bytes(8)
    result.extend(bytes(raw-len(result)))
    result.extend(payload)
    result.extend(bytes(raw_size-len(payload)))
    updated = pefile.PE(data=bytes(result))
    struct.pack_into('<I', result, pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'), updated.generate_checksum())
    OUTPUT.write_bytes(result)
    manifest = dict(
        source=SOURCE.name, output=OUTPUT.name, original_sha256=EXPECTED_SHA256,
        patched_sha256=hashlib.sha256(result).hexdigest(), section_rva=rva,
        section_size=len(payload), symbols=symbols, changes=records,
        signature='Original signature directory cleared in modified copy; original is untouched.'
    )
    (WORK/'patch_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    assert SOURCE.read_bytes() == original
    print(f'Created {OUTPUT.name}: {len(payload)} payload bytes, {len(changes)} instruction hooks')
    print(f'SHA256 {manifest["patched_sha256"]}')

if __name__ == '__main__':
    build()
