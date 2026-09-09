from pathlib import Path
import pefile,struct,subprocess
R=Path(__file__).resolve().parent;f=R/'runtime_test/SELECT_DELAYED_TRACE.exe';b=bytearray(f.read_bytes());p=pefile.PE(data=b);rva=p.OPTIONAL_HEADER.SizeOfImage
asm=f""".intel_syntax noprefix
.code32
.text
pushad
call loc
loc: pop edi
sub edi,{rva+6}
mov ebx,[edi+{rva+4096}]
cmp ebx,500
jae done
imul esi,ebx,16
lea esi,[edi+esi+{rva+4100}]
inc ebx
mov [edi+{rva+4096}],ebx
call dword ptr [edi+0x1c93f4]
mov [esi],eax
mov eax,[esp+36]
mov [esi+4],eax
mov eax,[esp+40]
movzx eax,byte ptr [eax]
mov [esi+8],eax
mov eax,[esp+44]
mov [esi+12],eax
done: popad
.byte 0xe9
.long 0x7bec-{rva}-(.-4)-4
"""
# Call the real stdcall API and retain its result and bytes-written count.
asm=asm[:asm.index('done: popad')]+f"""done:
push dword ptr [esp+52]
push dword ptr [esp+52]
push dword ptr [esp+52]
push dword ptr [esp+52]
push dword ptr [esp+52]
.byte 0xe8
.long 0x7bec-{rva}-(.-trace_start)-4
mov [esp+28],eax
cmp ebx,500
jae finished
mov edx,[esp+48]
mov edx,[edx]
shl edx,8
or eax,edx
mov [esi+12],eax
finished: popad
ret 20
"""
asm=asm.replace('.text\n','.text\ntrace_start:\n')
(R/'select_delayed_tx_trace.s').write_text(asm);subprocess.run(['as','--32','-o',str(R/'select_delayed_tx_trace.o'),str(R/'select_delayed_tx_trace.s')],check=True);subprocess.run(['objcopy','-O','binary','-j','.text',str(R/'select_delayed_tx_trace.o'),str(R/'select_delayed_tx_trace.bin')],check=True)
a=bytearray((R/'select_delayed_tx_trace.bin').read_bytes())
off=p.get_offset_from_rva(0x800db);assert b[off]==0xe8;b[off:off+5]=b'\xe8'+struct.pack('<i',rva-0x800e0)
last=p.sections[-1];raw=last.PointerToRawData+rva-last.VirtualAddress;b.extend(bytes(raw-len(b))+a+bytes(12288-len(a)))
struct.pack_into('<I',b,last.get_field_absolute_offset('Misc_VirtualSize'),rva-last.VirtualAddress+12288);struct.pack_into('<I',b,last.get_field_absolute_offset('SizeOfRawData'),rva-last.VirtualAddress+12288);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),rva+12288);struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),pefile.PE(data=b).generate_checksum());f.write_bytes(b);print('trace RVA',hex(rva+4096))
