.intel_syntax noprefix
.code32
.section .text
.global import_hook
import_hook:
 pushad
 call base
base:
 pop esi
 .byte 0x81,0xee
 .long PAYLOAD_RVA + base
 sub esp, 272
 mov edi, esp
 mov eax, [esi + PAYLOAD_RVA + entry_ptr]
 test eax,eax
 jnz invoke
 push 260
 push edi
 push 0
 call [esi+0x1c9228]
 test eax,eax
 jz failed
 cmp eax,240
 ja failed
 lea ecx,[edi+eax]
scan:
 cmp ecx,edi
 jbe failed
 dec ecx
 cmp byte ptr [ecx],92
 jne scan
 inc ecx
 lea edx,[esi+PAYLOAD_RVA+dll_name]
copy_name:
 mov al,[edx]
 mov [ecx],al
 inc ecx
 inc edx
 test al,al
 jnz copy_name
 push 8
 push 0
 push edi
 call [esi+0x1c9214]
 test eax,eax
 jz failed
 lea edx,[esi+PAYLOAD_RVA+export_name]
 push edx
 push eax
 call [esi+0x1c9220]
 test eax,eax
 jz failed
 mov [esi+PAYLOAD_RVA+entry_ptr],eax
invoke:
 push dword ptr [ebp-0x18]
 push dword ptr [ebx+0x14c]
 call eax
 test eax,eax
 jz legacy
handled:
 add esp,272
 popad
 jmp done_jump
legacy:
 add esp,272
 popad
 lea edx,[ebp-0x20]
 mov eax,[ebx+0x2e8]
 jmp legacy_jump
failed:
 push 0x10
 lea eax,[esi+PAYLOAD_RVA+title]
 push eax
 lea eax,[esi+PAYLOAD_RVA+failure]
 push eax
 push dword ptr [ebx+0x14c]
 call [esi+0x1c97a0]
 jmp handled
.align 4
entry_ptr: .long 0
dll_name: .asciz "SIT_Import.dll"
export_name: .asciz "SitImport"
title: .asciz "SAIV IT - Import"
failure: .asciz "Cannot load SIT_Import.dll. Keep this module beside the SIT executable."
