.intel_syntax noprefix
.code32
.text
.global after_modal, reopen
.set RVA,0x298000
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
 original 0x7e8f8
 push eax
 cmp byte ptr [ebp-3],1
 mov byte ptr [ebp-3],0
 jne open_done
 cmp byte ptr [esi+0x24],0
 je open_done
 image_base
 # Let the reopened adapter settle; Detect already waited for a complete menu.
 push 1100
 call dword ptr [edi+0x1c9358]
 mov eax,esi
 lea edx,[edi+RVA+(command_g-after_modal)]
 original 0x7ffc4
open_done:
 pop eax
 pop edi
 pop esi
 ret
.balign 4
.long -1,1
command_g: .asciz "G"

pending: .byte 0
