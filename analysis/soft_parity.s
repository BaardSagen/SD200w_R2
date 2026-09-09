.intel_syntax noprefix
.code32
.text
.global configure, receive, send_string
.set RVA,0x298000
.macro original rva
 .byte 0xe8
 .long \rva-RVA-(.-configure)-4
.endm
# stdcall SetCommState(handle, DCB*). Keep the logical DCB unchanged.
configure:
 push ebx
 push esi
 push edi
 sub esp,28
 mov esi,[esp+48]
 mov edi,esp
 mov ecx,7
 rep movsd
 and dword ptr [esp+8],0xffffffb3
 cmp byte ptr [esp+24],7
 jne configured
 cmp byte ptr [esp+25],2
 jne configured
 mov word ptr [esp+24],8
 and dword ptr [esp+8],0xfffffffd
configured:
 mov eax,[esp+44]
 push esp
 push eax
 original 0x7b5c
 add esp,28
 pop edi
 pop esi
 pop ebx
 ret 8
# The serial ReadFile call has EDI = serial object. No global/file I/O hook.
receive:
 push ebx
 push esi
 mov ebx,esp
 push dword ptr [ebx+28]
 push dword ptr [ebx+24]
 push dword ptr [ebx+20]
 push dword ptr [ebx+16]
 push dword ptr [ebx+12]
 original 0x7b4c
 test eax,eax
 jz received
 cmp byte ptr [edi+0x4c],'e'
 jne received
 cmp byte ptr [edi+0x4d],7
 jne received
 mov edx,[ebx+24]
 test edx,edx
 jz received
 mov ecx,[edx]
 cmp ecx,[ebx+20]
 ja received
 test ecx,ecx
 jz received
 mov esi,[ebx+16]
mask_byte:
 and byte ptr [esi],0x7f
 inc esi
 dec ecx
 jnz mask_byte
received:
 pop esi
 pop ebx
 ret 20
# Replace the existing UniqueString call before the serial WriteFile.
# EAX points to the caller's managed local, EBP is the SendString frame.
# Copy-on-write happens BEFORE encoding, preserving shared/literal commands.
send_string:
 original 0x43e8
 push eax
 test eax,eax
 jz encoded
 mov edx,[ebp-4]
 cmp byte ptr [edx+0x4c],'e'
 jne encoded
 cmp byte ptr [edx+0x4d],7
 jne encoded
 mov ecx,[eax-4]
 test ecx,ecx
 jz encoded
 mov edx,eax
encode_byte:
 mov al,[edx]
 and al,0x7f
 jp even_bits
 or al,0x80
even_bits:
 mov [edx],al
 inc edx
 dec ecx
 jnz encode_byte
encoded:
 pop eax
 ret
