.intel_syntax noprefix
.code32
.text
.global after_modal, reopen
.set RVA,0x29d000
.macro original target
 .byte 0xe8
 .long \target-RVA-(.-after_modal)-4
.endm
.macro image_base
 call 991f
991: pop edi
 sub edi,RVA+(991b-after_modal)
.endm
after_modal:
 pushad
 image_base
 call cancel_timer
 popad
 push eax
 push edx
 push edi
 image_base
 mov byte ptr [edi+RVA+(pending-after_modal)],0
 pop edi
 pop edx
 pop eax
 call dword ptr [edx+0xd8]
 push eax
 push edi
 image_base
 mov byte ptr [ebp-3],0
 cmp eax,1
 jne modal_done
 mov dl,[edi+RVA+(pending-after_modal)]
 mov [ebp-3],dl
 test dl,dl
 jz modal_done
 # Selecting SD200 explicitly opens its terminal connection, even if previously closed.
 mov byte ptr [ebp-1],1
modal_done:
 mov byte ptr [edi+RVA+(pending-after_modal)],0
 pop edi
 pop eax
 ret
capture_close:
 # Capture identity while workers still exist; original FormClose frees them.
 pushad
 image_base
 mov byte ptr [edi+RVA+(pending-after_modal)],0
 mov esi,[eax+0x330]
 test esi,esi
 jz capture_done
 mov ebx,[esi-4]
 test ebx,ebx
 jle capture_done
next_row:
 mov eax,[esi+16]
 test eax,eax
 jz advance
 cmp dword ptr [eax-4],5
 jne advance
 cmp dword ptr [eax],0x74736e49
 jne advance
 cmp byte ptr [eax+4],'r'
 jne advance
 mov eax,[esi]
 test eax,eax
 jz capture_done
 cmp byte ptr [eax+0x60],0
 jne capture_done
 cmp byte ptr [eax+0x62],1
 jne capture_done
 cmp byte ptr [eax+0x71],2
 jne capture_done
 mov ecx,[eax+0x64]
 mov cl,[ecx+0x34]
 mov [edi+RVA+(port-after_modal)],cl
 mov ecx,[eax+0x6c]
 mov [edi+RVA+(baud-after_modal)],ecx
 mov cl,[eax+0x70]
 mov [edi+RVA+(parity-after_modal)],cl
 mov edx,[eax+0x5c]
 original CLASSIFY
 cmp eax,3
 jne capture_done
 mov byte ptr [edi+RVA+(pending-after_modal)],1
 jmp capture_done
advance:
 add esi,20
 dec ebx
 jnz next_row
capture_done:
 popad
 push ebp
 mov ebp,esp
 push 0
 .byte 0xe9
 .long 0x111921-RVA-(.-after_modal)-4
reopen:
 push esi
 push edi
 mov esi,eax
 image_base
 cmp byte ptr [ebp-3],1
 jne original_open
 # Reopen the selected port, not the previous terminal port.
 mov eax,esi
 mov dl,[edi+RVA+(port-after_modal)]
 original 0x7e6c0
 # The detected format must already be correct if Detect was opened inside Setup.
 mov edx,[edi+RVA+(baud-after_modal)]
 mov [esi+0x30],edx
 mov dl,[edi+RVA+(parity-after_modal)]
 mov [esi+0x4c],dl
 mov byte ptr [esi+0x4d],8
 cmp dl,'e'
 jne original_open
 mov byte ptr [esi+0x4d],7
original_open:
 mov eax,esi
 original 0x7e8f8
 push eax
 cmp byte ptr [ebp-3],1
 mov byte ptr [ebp-3],0
 jne open_done
 cmp byte ptr [esi+0x24],0
 je open_done
 mov eax,[edi+0x1c8964]
 mov [edi+RVA+(main_form-after_modal)],eax
 lea eax,[edi+RVA+(timer_callback-after_modal)]
 push eax
 push 1100
 push 0
 push 0
 call dword ptr [edi+0x1c9708]
 mov [edi+RVA+(timer_id-after_modal)],eax
open_done:
 pop eax
 pop edi
 pop esi
 ret
cancel_timer:
 mov eax,[edi+RVA+(timer_id-after_modal)]
 test eax,eax
 jz cancel_done
 mov dword ptr [edi+RVA+(timer_id-after_modal)],0
 push eax
 push 0
 call dword ptr [edi+0x1c97c4]
cancel_done:
 ret
timer_callback:
 push ebp
 mov ebp,esp
 push ebx
 push esi
 push edi
 image_base
 mov eax,[ebp+16]
 cmp eax,[edi+RVA+(timer_id-after_modal)]
 jne callback_done
 test eax,eax
 jz callback_done
 call cancel_timer
 mov eax,[edi+0x1c8964]
 test eax,eax
 jz callback_done
 cmp eax,[edi+RVA+(main_form-after_modal)]
 jne callback_done
 mov esi,[eax+0x510]
 test esi,esi
 jz callback_done
 cmp byte ptr [esi+0x24],0
 je callback_done
 mov al,[esi+0x34]
 cmp al,[edi+RVA+(port-after_modal)]
 jne callback_done
 mov eax,[esi+0x30]
 cmp eax,[edi+RVA+(baud-after_modal)]
 jne callback_done
 mov al,[esi+0x4c]
 cmp al,[edi+RVA+(parity-after_modal)]
 jne callback_done
 mov eax,esi
 lea edx,[edi+RVA+(command_g-after_modal)]
 original 0x7ffc4
callback_done:
 pop edi
 pop esi
 pop ebx
 pop ebp
 ret 16
.balign 4
.long -1,1
command_g: .asciz "G"
pending: .byte 0
parity: .byte 0
port: .byte 0
.balign 4
baud: .long 0
main_form: .long 0
timer_id: .long 0
