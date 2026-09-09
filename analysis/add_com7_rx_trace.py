from pathlib import Path
import pefile,struct,subprocess
R=Path(__file__).resolve().parent;f=R/'runtime_test/COM7_NATIVE_DIAGNOSTIC.exe';b=bytearray(f.read_bytes());p=pefile.PE(data=b);rva=p.OPTIONAL_HEADER.SizeOfImage
asm=f""".intel_syntax noprefix
.code32
.text
trace_start:
push dword ptr [esp+20]
push dword ptr [esp+20]
push dword ptr [esp+20]
push dword ptr [esp+20]
push dword ptr [esp+20]
.byte 0xe8
.long 0x7b4c-{rva}-(.-trace_start)-4
pushad
mov edx,[esp+48]
cmp dword ptr [edx],0
jne record
cmp dword ptr [esp+28],0
jne done
record:
call loc
loc: pop edi
sub edi,{rva}+(loc-trace_start)
mov ebx,[edi+{rva+4096}]
cmp ebx,500
jae done
imul esi,ebx,32
lea esi,[edi+esi+{rva+4100}]
inc ebx
mov [edi+{rva+4096}],ebx
call dword ptr [edi+0x1c93f4]
mov [esi],eax
mov eax,[esp+36]
mov [esi+4],eax
mov eax,[esp+48]
mov eax,[eax]
mov [esi+8],eax
mov eax,[esp+28]
mov [esi+12],eax
mov edx,[esp+40]
mov eax,[edx]
mov [esi+16],eax
mov eax,[edx+4]
mov [esi+20],eax
mov eax,[edx+8]
mov [esi+24],eax
mov eax,[edx+12]
mov [esi+28],eax
done: popad
ret 20
"""
(R/'com7_rx_trace.s').write_text(asm);subprocess.run(['as','--32','-o',str(R/'com7_rx_trace.o'),str(R/'com7_rx_trace.s')],check=True);subprocess.run(['objcopy','-O','binary','-j','.text',str(R/'com7_rx_trace.o'),str(R/'com7_rx_trace.bin')],check=True)
a=(R/'com7_rx_trace.bin').read_bytes();off=p.get_offset_from_rva(0x7fc73);b[off:off+5]=b'\xe8'+struct.pack('<i',rva-0x7fc78)
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;size=24576;b.extend(bytes(raw-len(b))+a+bytes(size-len(a)))
struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+size);struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+size);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),rva+size);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=b).generate_checksum());f.write_bytes(b);print('RX trace RVA',hex(rva+4096))
