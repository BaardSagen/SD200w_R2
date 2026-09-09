.intel_syntax noprefix
.code32
.text
.global start, receive, timer_callback, state, received, main_form, port, message
.set RVA,0x299000
.macro base
 call 991f
991: pop edi
 sub edi,RVA+(991b-start)
.endm
.macro original target
 .byte 0xe8
 .long \target-RVA-(.-start)-4
.endm
start:
 original 0x1a0ff0
 pushfd
 pushad
 base
 cmp byte ptr [edi+RVA+(state-start)],0
 jne start_done
 mov eax,[edi+0x1c8964]
 test eax,eax
 jz start_done
 mov [edi+RVA+(main_form-start)],eax
 mov eax,[eax+0x510]
 mov al,[eax+0x34]
 mov [edi+RVA+(port-start)],al
 mov byte ptr [edi+RVA+(state-start)],1
 lea eax,[edi+RVA+(timer_callback-start)]
 push eax
 push 3000
 push 0
 push 0
 call dword ptr [edi+0x1c9708]
 test eax,eax
 jnz start_done
 mov byte ptr [edi+RVA+(state-start)],2
start_done:
 popad
 popfd
 ret
receive:
 pushfd
 pushad
 base
 mov byte ptr [edi+RVA+(received-start)],1
 popad
 popfd
 # Preserve existing disk-refresh receive handling.
 .byte 0xe9
 .long 0x292000-RVA-(.-start)-4
timer_callback:
 push ebp
 mov ebp,esp
 push ebx
 push esi
 push edi
 base
 push dword ptr [ebp+16]
 push 0
 call dword ptr [edi+0x1c97c4]
 cmp byte ptr [edi+RVA+(state-start)],1
 jne done
 mov byte ptr [edi+RVA+(state-start)],2
 cmp byte ptr [edi+RVA+(received-start)],0
 jne done
 mov ebx,[edi+RVA+(main_form-start)]
 test ebx,ebx
 jz done
 cmp ebx,[edi+0x1c8964]
 jne done
 mov eax,[ebx+0x510]
 mov al,[eax+0x34]
 cmp al,[edi+RVA+(port-start)]
 jne done
 mov eax,ebx
 lea edx,[edi+RVA+(message-start)]
 xor ecx,ecx
 original 0x19bbd4
 mov byte ptr [ebx+0xb10],1
 # Repaint the terminal; text is local UI history, never serial TX.
 mov eax,[ebx+0x44c]
 mov edx,[eax]
 call dword ptr [edx+0x74]
done:
 pop edi
 pop esi
 pop ebx
 pop ebp
 ret 16
state: .byte 0
received: .byte 0
port: .byte 0
.balign 4
main_form: .long 0
.long -1,71
message: .asciz "Hold <I> to wake the instrument, or use Detect to find connected units."
