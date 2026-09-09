.intel_syntax noprefix
.code32
.text
.global save_last_port
save_last_port:
 pushfd
 pushad
 call here
here:
 pop edi
 sub edi,PAYLOAD_RVA+(here-save_last_port)
 mov eax,[edi+0x1c8964]
 test eax,eax
 jz done
 mov esi,[eax+0x510]
 test esi,esi
 jz done
 cmp byte ptr [esi+0x407e],0
 jne done
 movzx edx,byte ptr [esi+0x34]
 test edx,edx
 jz done
 mov eax,[ebp-0x18]
 test eax,eax
 jz done
 push edx
 lea edx,[edi+0x1152e8]
 lea ecx,[edi+0x1152b8]
 mov ebx,[eax]
 call dword ptr [ebx+0xc]
done:
 popad
 popfd
 # Continue the existing Show startup text hook and its original replay.
 .byte 0xe9
 .long PREVIOUS_RVA-PAYLOAD_RVA-(.-save_last_port)-4
