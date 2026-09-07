"""Execute the patched x86 hooks in Unicorn; never opens a real COM port."""
from pathlib import Path
import hashlib
import json
import random
import struct
import sys
import unittest

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent
sys.path.insert(0, str(WORK/'python_packages'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *

MANIFEST = json.loads((WORK/'patch_manifest.json').read_text())
SYMBOLS = MANIFEST['symbols']
REGS = [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX,
        UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP]

class Harness:
    MAIN = 0x10001000
    DIALOG = 0x10003000
    TIMER = 0x10005000
    BUTTON = 0x10006000
    LOG_BUTTON = 0x10007000
    COMM = 0x10008000
    AUX = 0x1000d000
    INPUT = 0x10012000
    STACK = 0x2000f000
    RETURN = 0x1001f000

    def __init__(self, base=0x400000):
        self.base = base
        pe = pefile.PE(str(ROOT/'SD200W_diskguard.exe'))
        if base != pe.OPTIONAL_HEADER.ImageBase:
            pe.relocate_image(base)
        self.uc = Uc(UC_ARCH_X86, UC_MODE_32)
        self.uc.mem_map(base, pe.OPTIONAL_HEADER.SizeOfImage)
        self.uc.mem_write(base, bytes(pe.get_memory_mapped_image()))
        self.uc.mem_map(0x10000000, 0x20000)
        self.uc.mem_map(0x20000000, 0x10000)
        self.messages = []
        self.timer_calls = []
        self.stops = set()
        self.stopped = None
        self.put32(self.get32(base+0x1b2174), self.MAIN)
        self.put32(self.get32(base+0x1b21e0), self.DIALOG)
        self.put32(self.MAIN+0x374, self.BUTTON)
        self.put32(self.MAIN+0x510, self.COMM)
        self.put32(self.DIALOG+0x3fc, self.TIMER)
        self.put32(base+0x1c97a0, self.RETURN-0x100)
        self.uc.hook_add(UC_HOOK_CODE, self.hook)

    def put32(self, a, v): self.uc.mem_write(a, struct.pack('<I', v))
    def get32(self, a): return struct.unpack('<I', self.uc.mem_read(a, 4))[0]
    def byte(self, a, v=None):
        if v is not None: self.uc.mem_write(a, bytes([v]))
        return self.uc.mem_read(a, 1)[0]
    def state_addr(self, name): return self.base+MANIFEST['section_rva']+SYMBOLS[name]
    def state(self, name, v=None): return self.byte(self.state_addr(name), v)
    def cstring(self, a):
        s = bytearray()
        while self.byte(a):
            s.append(self.byte(a)); a += 1
            assert len(s) < 200
        return s.decode('ascii')
    def ret(self, cleanup=0):
        sp = self.uc.reg_read(UC_X86_REG_ESP)
        self.uc.reg_write(UC_X86_REG_EIP, self.get32(sp))
        self.uc.reg_write(UC_X86_REG_ESP, sp+4+cleanup)
    def hook(self, uc, address, size, unused):
        if address in self.stops:
            self.stopped = address
            uc.emu_stop()
        elif address == self.base+0x61250:
            self.timer_calls.append((uc.reg_read(UC_X86_REG_EAX),uc.reg_read(UC_X86_REG_EDX)&255))
            self.ret()
        elif address == self.RETURN-0x100:
            sp = uc.reg_read(UC_X86_REG_ESP)
            self.messages.append(self.cstring(self.get32(sp+8)))
            assert self.get32(sp+4) == 0
            assert self.get32(sp+16) == 0x2040
            self.ret(16)
        elif not (self.base+MANIFEST['section_rva'] <= address < self.base+MANIFEST['section_rva']+MANIFEST['section_size'] or
                  address in {self.base+r for r in [0x19b308,0x1a14f4,0x1a156f,0x7f9c4]}):
            raise AssertionError(f'Unexpected execution outside hook: {address:#x}')

    def run(self, rva, stops, eax=0, edx=0, ebx=0x76543210):
        initial = [eax, ebx, 0x12345678, edx, 0x13572468, 0x24681357, 0x20001000]
        for reg, value in zip(REGS, initial): self.uc.reg_write(reg, value)
        self.uc.reg_write(UC_X86_REG_ESP, self.STACK)
        self.uc.reg_write(UC_X86_REG_EFLAGS, 0x246)
        self.put32(self.STACK, self.RETURN)
        self.stops = {self.base+r for r in stops} | {self.RETURN}
        self.stopped = None
        self.uc.emu_start(self.base+rva, 0, count=10000)
        assert self.stopped is not None, 'Hook did not return in bounded time'
        return self.stopped

    def receive(self, text):
        if isinstance(text, str): text = text.encode('ascii')
        for c in text:
            self.byte(self.INPUT, c)
            self.run(0x19b308, [0x19b30e], eax=self.INPUT, edx=1)
            assert self.uc.reg_read(UC_X86_REG_ESP) == self.STACK
            assert self.uc.reg_read(UC_X86_REG_EBX) == (0x76543200|c)
            assert self.uc.reg_read(UC_X86_REG_EAX) == (0x76543200|c)
            assert self.uc.reg_read(UC_X86_REG_ECX) == 0x12345678
            assert self.uc.reg_read(UC_X86_REG_EDX) == 1
            assert self.uc.reg_read(UC_X86_REG_ESI) == 0x13572468
            assert self.uc.reg_read(UC_X86_REG_EDI) == 0x24681357
            assert self.uc.reg_read(UC_X86_REG_EFLAGS) == 0x246

    def click(self, log=False):
        return self.run(0x1a14f4, [0x1a14fa], eax=self.MAIN,
                        edx=self.LOG_BUTTON if log else self.BUTTON)
    def active(self, log=False):
        self.byte(self.DIALOG+0xa60, int(log))
        self.byte(self.DIALOG+0xa61, 1)

class GuardTests(unittest.TestCase):
    def test_full_device_response_aborts_and_shows_message(self):
        for base in [0x400000, 0x1400000]:
            with self.subTest(base=hex(base)):
                h = Harness(base)
                self.assertEqual(h.click(), base+0x1a14fa)
                h.active()
                h.receive('Data logged by the SAIU110 is stored on its internal disk.\r\n'
                          'When the device is connected to a PC, the disk normally appears automatically in File Explorer.\r\n'
                          'Stop logging before refreshing the disk. Refreshing is blocked while logging is active.\r\n'
                          'Refresh disk Y/N')
                self.assertEqual(h.state('blocked'), 1)
                self.assertEqual(h.state('pending'), 1)
                self.assertEqual(h.byte(h.DIALOG+0xa61), 0)
                self.assertEqual(h.byte(h.DIALOG+0xa62), 1)
                self.assertEqual(h.byte(h.DIALOG+0xa63), 1)
                self.assertEqual(h.get32(h.DIALOG+0x234), 2)
                self.assertEqual(h.timer_calls, [(h.TIMER,0)])
                self.assertEqual(h.messages, []) # UI notification is deferred until ShowModal returns.
                self.assertEqual(h.run(0x1a156f, [0x1a15c7,0x1a1574,0x1a1586], eax=2), base+0x1a15c7)
                self.assertEqual(h.messages, ['Download virker ikke i denne modusen'])
                self.assertEqual(h.state('pending'),0)
                self.assertEqual(h.state('requested'),0)
                self.assertEqual(h.uc.reg_read(UC_X86_REG_ESP), h.STACK)

    def test_known_mode_blocks_click_without_starting_download(self):
        h = Harness()
        h.receive('Refresh disk Y/N')
        self.assertEqual(h.click(), h.RETURN)
        self.assertEqual(h.messages, ['Download virker ikke i denne modusen'])
        self.assertEqual(h.uc.reg_read(UC_X86_REG_ESP), h.STACK+4)
        self.assertEqual(h.state('requested'),0)

    def test_normal_measurements_and_original_modal_branches(self):
        h = Harness(); h.click(); h.active()
        h.receive('SAIU110 Surface logger\r\nMenu:\r\nN0001 10.42 3.12\r\nN0002 10.41 3.10\r\n')
        self.assertEqual(h.byte(h.DIALOG+0xa61),1)
        self.assertEqual(h.state('blocked'),0)
        self.assertEqual(h.timer_calls,[])
        self.assertEqual(h.messages,[])
        for result, expected in [(2,0x1a1574),(1,0x1a1586),(0,0x1a1586)]:
            self.assertEqual(h.run(0x1a156f,[0x1a1574,0x1a1586,0x1a15c7],eax=result),h.base+expected)
            self.assertEqual(h.uc.reg_read(UC_X86_REG_EAX),result)

    def test_log_button_uses_original_path(self):
        h = Harness(); h.receive('Refresh disk Y/N')
        self.assertEqual(h.click(log=True), h.base+0x1a14fa)
        h.active(log=True); h.receive('Refresh disk Y/N')
        self.assertEqual(h.byte(h.DIALOG+0xa61),1)
        self.assertEqual(h.state('pending'),0)
        self.assertEqual(h.messages,[])

    def test_reconnect_resets_mode_but_auxiliary_close_does_not(self):
        h = Harness(); h.receive('Refresh disk Y/N')
        h.run(0x7f9c4,[0x7f9c9],eax=h.AUX)
        self.assertEqual(h.state('blocked'),1)
        h.run(0x7f9c4,[0x7f9c9],eax=h.COMM)
        self.assertEqual(h.state('blocked'),0)
        self.assertEqual(h.state('matcher'),0)
        self.assertEqual(h.click(),h.base+0x1a14fa)

    def test_variants_partial_matches_and_no_false_positives(self):
        for text in ['refresh disk y/n', 'REFRESH DISK Y/N', 'ReFrEsH\r\n disk\tY / N',
                     'refrefresh disk y/n', 'refresh refresh disk y/n']:
            with self.subTest(text=text):
                h=Harness(); h.receive(text); self.assertEqual(h.state('blocked'),1)
        for text in ['Refresh disk', 'Refresh disk Y/', 'Refresh disk Y/X',
                     'Refresh disk Y/N is unsupported'.replace('Y/N','Y-X'),
                     'Refreshing is blocked while logging is active.']:
            with self.subTest(text=text):
                h=Harness(); h.receive(text); self.assertEqual(h.state('blocked'),0)

    def test_every_chunk_boundary(self):
        text='Refresh disk Y/N'
        for split in range(len(text)+1):
            h=Harness(); h.receive(text[:split]); h.receive(text[split:])
            self.assertEqual(h.state('blocked'),1)

    def test_partial_match_cannot_cross_reconnection(self):
        h=Harness(); h.receive('Refresh disk Y/')
        h.run(0x7f9c4,[0x7f9c9],eax=h.COMM)
        h.receive('N'); self.assertEqual(h.state('blocked'),0)

    def test_stream_matcher_against_reference(self):
        rng=random.Random(17)
        for _ in range(30):
            text=''.join(rng.choice('refshdiky/nXYZ \r\n') for _ in range(120))
            if rng.randrange(2): text += 'reFReSh disk Y/n'
            compact=''.join(c.lower() for c in text if c not in ' \t\r\n')
            h=Harness(); h.receive(text)
            self.assertEqual(bool(h.state('blocked')),'refreshdisky/n' in compact)

    def test_pe_structure_and_original_preservation(self):
        original=(ROOT/'SD200W.exe').read_bytes()
        modified=(ROOT/'SD200W_diskguard.exe').read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(),MANIFEST['original_sha256'])
        self.assertEqual(hashlib.sha256(modified).hexdigest(),MANIFEST['patched_sha256'])
        old=pefile.PE(data=original); new=pefile.PE(data=modified)
        self.assertEqual(new.OPTIONAL_HEADER.CheckSum,new.generate_checksum())
        self.assertEqual(len(new.sections),len(old.sections)+1)
        self.assertEqual(new.OPTIONAL_HEADER.DATA_DIRECTORY[4].Size,0)
        permitted=set()
        for c in MANIFEST['changes']: permitted.update(range(c['offset'],c['offset']+len(bytes.fromhex(c['original']))))
        for a,b in zip(old.sections,new.sections):
            self.assertEqual(a.__pack__(),b.__pack__())
            for offset in range(a.PointerToRawData,a.PointerToRawData+a.SizeOfRawData):
                if offset not in permitted: self.assertEqual(original[offset],modified[offset])
        for index in [0,1,2,3,5,9,12]:
            self.assertEqual(old.OPTIONAL_HEADER.DATA_DIRECTORY[index].__pack__(),new.OPTIONAL_HEADER.DATA_DIRECTORY[index].__pack__())

if __name__=='__main__': unittest.main(verbosity=2)
