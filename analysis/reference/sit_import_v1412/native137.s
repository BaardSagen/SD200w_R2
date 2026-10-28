.intel_syntax noprefix
.code32
.text
.global entry, import_file, open_dialog, dispatch
.macro base
 call 991f
991: pop edi
 sub edi,RVA+(991b-entry)
.endm
.macro jump target
 .byte 0xe9
 .long \target-RVA-(.-entry)-4
.endm
entry:
import_file:
 pushfd
 pushad
 base
 cmp byte ptr [edi+ASCII_MODE],1
 jne import_old
 push 0
 push dword ptr [ebp-0x18]
 push ebx
 push 1
 call dispatch
 test eax,eax
 jz import_old
 popad
 popfd
 jump 0x1a5b39
import_old:
 popad
 popfd
 jump OLD_IMPORT_FILE
open_dialog:
 pushfd
 pushad
 push 0
 push 0
 push eax
 push 9
 call dispatch
 test eax,eax
 jz dialog_old
 popad
 popfd
 mov eax,1
 jmp dialog_done
dialog_old:
 popad
 popfd
 call dword ptr [edx+0x3c]
dialog_done:
 test al,al
 jump 0x1a0a49
# Export call dispatcher preserves its caller's parameter stack.
dispatch:
 push ebp
 mov ebp,esp
 pushad
 base
 mov eax,[edi+RVA+entry_ptr-entry]
 test eax,eax
 jnz dispatch_ready
 sub esp,272
 mov esi,esp
 push 260
 push esi
 push 0
 call [edi+0x1c9228]
 test eax,eax
 jz dispatch_failed
 cmp eax,240
 ja dispatch_failed
 lea ecx,[esi+eax]
scan:
 cmp ecx,esi
 jbe dispatch_failed
 dec ecx
 cmp byte ptr [ecx],92
 jne scan
 inc ecx
 lea edx,[edi+RVA+dll_name-entry]
copy_name:
 mov al,[edx]
 mov [ecx],al
 inc ecx
 inc edx
 test al,al
 jnz copy_name
 push 8
 push 0
 push esi
 call [edi+0x1c9214]
 test eax,eax
 jz dispatch_failed
 lea edx,[edi+RVA+export_name-entry]
 push edx
 push eax
 call [edi+0x1c9220]
 mov [edi+RVA+entry_ptr-entry],eax
 add esp,272
 jmp dispatch_ready
dispatch_failed:
 add esp,272
 xor eax,eax
dispatch_ready:
 mov [esp+28],eax
 popad
 pop ebp
 test eax,eax
 jz dispatch_unavailable
 jmp eax
dispatch_unavailable:
 xor eax,eax
 ret 16
.balign 4
entry_ptr:.long 0
dll_name:.asciz "SIT_Import137.dll"
export_name:.asciz "SitNative"
