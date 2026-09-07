.intel_syntax noprefix
.code32
.text
.global passive, recognize, label, classify, fallback, cancelled, delayed_open
.set RVA,0x283000
.macro original rva
 .byte 0xe8
 .long \rva-RVA-(.-passive)-4
.endm
.macro base
 call 991f
991: pop edi
 sub edi,RVA+(991b-passive)
.endm
passive:
 push esi
 push edi
 push edx
 mov esi,75
listen:
 mov eax,[ebx+0x64]
 lea edx,[ebp-4] # Existing managed string local in search function.
 original 0x7fbc0
 test al,al
 jz pause
 lea eax,[ebx+0x58]
 mov edx,[ebp-4]
 original 0x4220
 mov edx,[ebx+0x58]
 call classify
 test eax,eax
 jnz found
pause:
 cmp byte ptr [ebx+0xc],0 # Thread termination / Cancel.
 jne cancelled
 push 20
 original 0x7bb4 # Windows Sleep, stdcall.
 dec esi
 jnz listen
fallback:
 pop edx # Original AT request after the passive listening period.
 mov eax,[ebx+0x64]
 original 0x7ffc4
 pop edi
 pop esi
 ret
found:
 lea eax,[ebx+0x5c]
 mov edx,[ebx+0x58]
 original 0x3fec
 mov eax,[ebx+0x64]
 mov edx,[eax+0x30]
 mov [ebx+0x6c],edx
 mov dl,[eax+0x4c]
 mov [ebx+0x70],dl
 mov byte ptr [ebx+0x62],1 # Mark communication successful so Execute does not replace type with Busy.
 mov byte ptr [ebx+0x71],2
cancelled:
 mov byte ptr [ebx+0x60],0
 pop edx
 pop edi
 pop esi
 ret
recognize:
 push eax
 push edx
 call classify
 test eax,eax
 pop edx
 pop eax
 jz legacy_recognize
 mov eax,1
 ret
legacy_recognize:
 .byte 0xe9
 .long 0x4504-RVA-(.-passive)-4
label:
 cmp byte ptr [eax+0x71],2
 jne legacy_label
 push eax
 push edx
 mov edx,[eax+0x5c]
 call classify
 test eax,eax
 jz label_restore
 push edi
 base
 lea edx,[edi+RVA+(osu_name-passive)]
 cmp eax,1
 je assign
 lea edx,[edi+RVA+(surface_name-passive)]
assign:
 mov eax,[esp+4]
 original 0x3fec
 pop edi
 pop edx
 pop eax
 ret
label_restore:
 pop edx
 pop eax
legacy_label:
 push ebx
 mov ebx,edx
 movzx eax,byte ptr [eax+0x71]
 .byte 0xe9
 .long 0x1031b7-RVA-(.-passive)-4
# Case-insensitive full banner phrase anywhere in the accumulated input.
classify:
 push ebx
 push ecx
 push edx
 push esi
 push edi
 test edx,edx
 jz missing
 mov esi,edx
 base
scan:
 cmp byte ptr [esi],0
 je missing
 lea ebx,[edi+RVA+(osu_banner-passive)]
 call prefix
 test eax,eax
 jnz match_osu
 lea ebx,[edi+RVA+(surface_banner-passive)]
 call prefix
 test eax,eax
 jnz match_surface
 inc esi
 jmp scan
match_osu:
 mov eax,1
 jmp classify_done
match_surface:
 mov eax,2
 jmp classify_done
missing:
 xor eax,eax
classify_done:
 pop edi
 pop esi
 pop edx
 pop ecx
 pop ebx
 ret
prefix:
 xor ecx,ecx
prefix_loop:
 mov al,[ebx+ecx]
 test al,al
 jz prefix_yes
 mov dl,[esi+ecx]
 test dl,dl
 jz prefix_no
 or dl,0x20
 cmp al,dl
 jne prefix_no
 inc ecx
 jmp prefix_loop
prefix_yes:
 mov eax,1
 ret
prefix_no:
 xor eax,eax
 ret
osu_banner: .asciz "osu107 instrument logger"
surface_banner: .asciz "saiv110 surface logger"
.balign 4
.long -1,6
osu_name: .asciz "OSU107"
.balign 4
.long -1,7
surface_name: .asciz "SAIV110"

delayed_open:
 push eax
 push edx
 push 1000
 original 0x7bb4
 pop edx
 pop eax
 .byte 0xe9
 .long 0x7e904-RVA-(.-passive)-4
