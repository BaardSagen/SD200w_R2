.intel_syntax noprefix
.code32
.text
.global read_option, write_option, setup_show, timer_gate, enabled, find_checkbox
.set RVA,0x29a000
.macro base
 call 991f
991: pop edi
 sub edi,RVA+(991b-read_option)
.endm
read_option:
 push dword ptr [esp+4]
 call dword ptr [ebx+8]
 pushad
 base
 push 1
 mov eax,[ebp-0x28]
 lea ecx,[edi+RVA+(key-read_option)]
 lea edx,[edi+0x197890]
 mov ebx,[eax]
 call dword ptr [ebx+8]
 test eax,eax
 setne byte ptr [edi+RVA+(enabled-read_option)]
 popad
 mov edx,[ebp-4]
 ret 4
write_option:
 pushad
 base
 mov eax,[ebp-4]
 call find_checkbox
 test eax,eax
 jz write_done
 mov edx,[eax]
 call dword ptr [edx+0xb4]
 mov [edi+RVA+(enabled-read_option)],al
 movzx eax,al
 push eax
 mov eax,[ebp-0x18]
 lea ecx,[edi+RVA+(key-read_option)]
 lea edx,[edi+0x1152e8]
 mov ebx,[eax]
 call dword ptr [ebx+0xc]
write_done:
 popad
 mov eax,[ebp-4]
 mov eax,[eax+0x300]
 ret
setup_show:
 pushad
 base
 call find_checkbox
 test eax,eax
 jz show_done
 mov dl,[edi+RVA+(enabled-read_option)]
 mov ecx,[eax]
 call dword ptr [ecx+0xb8]
show_done:
 popad
 push ebp
 mov ebp,esp
 mov ecx,9
 .byte 0xe9
 .long 0x1131c4-RVA-(.-read_option)-4
find_checkbox:
 push ebx
 push esi
 # TComponent.FComponents is a TList of owned components.
 mov eax,[eax+0x10]
 test eax,eax
 jz not_found
 mov ebx,[eax+8]
 cmp ebx,4096
 ja not_found
 mov esi,[eax+4]
 test esi,esi
 jz not_found
scan:
 test ebx,ebx
 jz not_found
 mov eax,[esi]
 test eax,eax
 jz next
 mov edx,[eax+8]
 test edx,edx
 jz next
 cmp dword ptr [edx-4],13
 jne next
 cmp dword ptr [edx],0x74536263
 jne next
 cmp dword ptr [edx+4],0x75747261
 jne next
 cmp dword ptr [edx+8],0x78655470
 jne next
 cmp byte ptr [edx+12],'t'
 je found
next:
 add esi,4
 dec ebx
 jmp scan
not_found:
 xor eax,eax
found:
 pop esi
 pop ebx
 ret
timer_gate:
 pushfd
 pushad
 base
 cmp byte ptr [edi+RVA+(enabled-read_option)],0
 jne gate_done
 mov byte ptr [edi+HINT_STATE],2
gate_done:
 popad
 popfd
 .byte 0xe9
 .long HINT_CALLBACK-RVA-(.-read_option)-4
enabled: .byte 1
.balign 4
.long -1,15
key: .asciz "ShowStartupText"
