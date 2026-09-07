"""Hide and disconnect Call/Receive in the already tested diskguard copy."""
from pathlib import Path
import hashlib
import json
import struct
import pefile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'SD200W_diskguard.exe'
OUTPUT = ROOT / 'SD200W_diskguard_no_call_receive.exe'
EXPECTED = '7279a7e1dd73227b47574ef2d2ff820f423c69021d5b08b8ea6bd2cb56cc22e4'
TARGETS = {'btnPhone', 'btnPhoneAnswer'}

class DfmReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.nodes = {}

    def take(self, n):
        result = self.data[self.pos:self.pos+n]
        assert len(result) == n
        self.pos += n
        return result

    def byte(self):
        return self.take(1)[0]

    def string(self):
        return self.take(self.byte()).decode('latin1')

    def value(self):
        tag = self.byte()
        if tag in (0,8,9,13):
            return
        if tag == 1:
            while self.data[self.pos]: self.value()
            self.byte()
        elif tag in (2,3,4,5,15,16,19,21):
            self.take({2:1,3:2,4:4,5:10,15:4,16:8,19:8,21:8}[tag])
        elif tag in (6,7):
            self.string()
        elif tag in (10,12,20):
            self.take(struct.unpack('<I',self.take(4))[0])
        elif tag == 18:
            self.take(2*struct.unpack('<I',self.take(4))[0])
        elif tag == 11:
            while self.string(): pass
        elif tag == 14:
            while self.data[self.pos]:
                # Collection items start with vaList and may have an integer ID.
                if self.data[self.pos] in (2,3,4): self.value()
                assert self.byte() == 1
                while self.string(): self.value()
            self.byte()
        else:
            raise ValueError(f'Unknown DFM value {tag} at {self.pos-1:#x}')

    def component(self):
        if self.data[self.pos] & 0xf0 == 0xf0:
            flags = self.byte() & 0xf
            if flags & 2: self.value()
        cls = self.string()
        name = self.string()
        properties = []
        while True:
            start = self.pos
            key = self.string()
            if not key: break
            value_start = self.pos
            self.value()
            properties.append((key,start,value_start,self.pos))
        self.nodes[name] = (cls,properties,start)
        while self.data[self.pos]: self.component()
        self.byte()

    def parse(self):
        assert self.take(4) == b'TPF0'
        self.component()
        assert self.pos == len(self.data), (self.pos,len(self.data))
        return self.nodes

original = SOURCE.read_bytes()
assert hashlib.sha256(original).hexdigest() == EXPECTED
pe = pefile.PE(data=original)
entries = [lang.data.struct
           for typ in pe.DIRECTORY_ENTRY_RESOURCE.entries if typ.id == 10
           for name in typ.directory.entries if str(name.name) == 'TFORM1'
           for lang in name.directory.entries]
assert len(entries) == 1
entry = entries[0]
dfm = pe.get_data(entry.OffsetToData,entry.Size)
nodes = DfmReader(dfm).parse()
edits = []
for name in TARGETS:
    cls, properties, end = nodes[name]
    assert cls == 'TSpeedButton'
    keys = {key for key,_,_,_ in properties}
    assert 'Glyph.Data' in keys and 'OnClick' in keys
    for key,start,value_start,stop in properties:
        if key in ('Glyph.Data','OnClick','Visible','Enabled'):
            edits.append((start,stop,b''))
    edits.append((end,end,b'\x07Visible\x08\x07Enabled\x08'))
patched = dfm
for start,end,replacement in sorted(edits,reverse=True):
    patched = patched[:start]+replacement+patched[end:]
updated_nodes = DfmReader(patched).parse()
assert nodes.keys() == updated_nodes.keys()
for name,(cls,properties,_) in nodes.items():
    def values(blob, props):
        return {key:blob[v:end] for key,_,v,end in props}
    before = values(dfm,properties)
    after = values(patched,updated_nodes[name][1])
    if name in TARGETS:
        before.pop('Glyph.Data')
        before.pop('OnClick')
        before.update(Visible=b'\x08',Enabled=b'\x08')
    assert before == after, name
result = bytearray(original)
offset = pe.get_offset_from_rva(entry.OffsetToData)
result[offset:offset+entry.Size] = patched + bytes(entry.Size-len(patched))
struct.pack_into('<I',result,entry.get_field_absolute_offset('Size'),len(patched))
checksum_offset = pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
updated_pe = pefile.PE(data=bytes(result))
struct.pack_into('<I',result,checksum_offset,updated_pe.generate_checksum())
OUTPUT.write_bytes(result)
check = pefile.PE(str(OUTPUT))
assert check.OPTIONAL_HEADER.CheckSum == check.generate_checksum()
# All executable sections, including the existing download guard, stay byte identical.
for section in pe.sections:
    if section.Characteristics & 0x20000000:
        a=section.PointerToRawData; b=a+section.SizeOfRawData
        assert original[a:b] == result[a:b]
assert SOURCE.read_bytes() == original
report = dict(source=SOURCE.name,output=OUTPUT.name,source_sha256=EXPECTED,
              output_sha256=hashlib.sha256(result).hexdigest(),hidden_buttons=sorted(TARGETS),
              verification='Both DFMs parsed completely; only target properties differ; all executable sections unchanged.',
              original_resource_size=len(dfm),modified_resource_size=len(patched))
(ROOT/'analysis'/'no_call_receive_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
