.intel_syntax noprefix
.code32
.text
.global probe, classify
.set RVA,0x297000
.macro original rva
 .byte 0xe8
 .long \rva-RVA-(.-probe)-4
.endm
.macro base
 call 991f
991: pop edi
 sub edi,RVA+(991b-probe)
.endm
.macro contains label
 lea ecx,[edi+RVA+(\label-probe)]
 call substring
.endm
probe:
 push ebx
 push esi
 push edi
 sub esp,24
 base
 call dword ptr [edi+0x1c93f4]
 mov [esp],eax
 mov [esp+4],eax
 mov [esp+12],eax
 mov dword ptr [esp+8],0
loop:
 cmp byte ptr [ebx+0xc],0
 jne cancelled
 cmp byte ptr [ebx+0x60],0
 je cancelled
 mov eax,[ebx+0x64]
 lea edx,[ebp-4]
 original 0x7fbc0
 test al,al
 jz evaluate
 mov eax,[ebp-4]
 test eax,eax
 jz evaluate
 cmp dword ptr [eax-4],0
 je evaluate
 lea eax,[ebx+0x58]
 mov edx,[ebp-4]
 original 0x4220
 call dword ptr [edi+0x1c93f4]
 mov [esp+4],eax
 mov eax,[ebx+0x58]
 cmp dword ptr [eax-4],16384
 ja failure
 # Switch the open UART to native 7E1 immediately; reopening loses the menu.
 mov edx,[ebx+0x64]
 cmp byte ptr [edx+0x4c],'n'
 jne evaluate
 mov ecx,[eax-4]
check_high_bit:
 test byte ptr [eax],0x80
 jnz native_even
 inc eax
 dec ecx
 jnz check_high_bit
 jmp evaluate
native_even:
 sub esp,28
 mov dword ptr [esp],28
 mov esi,[ebx+0x64]
 push esp
 push dword ptr [esi+0x2c]
 original 0x796c
 test eax,eax
 jz native_failed
 mov byte ptr [esp+18],7
 mov byte ptr [esp+19],2
 mov byte ptr [esp+20],0
 push esp
 push dword ptr [esi+0x2c]
 original 0x293000
 test eax,eax
 jz native_failed
 mov byte ptr [esi+0x4c],'e'
 mov byte ptr [esi+0x4d],7
 mov byte ptr [esi+0x4e],1
 mov dword ptr [ebx+0x40],1
 add esp,28
 lea eax,[ebx+0x58]
 original 0x3f98
 jmp loop
native_failed:
 add esp,28
 jmp failure
evaluate:
 call dword ptr [edi+0x1c93f4]
 mov esi,eax
 sub eax,[esp]
 cmp eax,15000
 jae failure
 mov edx,[ebx+0x58]
 call classify
 mov [esp+16],eax
 # Logger identity is passive; no serial command is required.
 cmp eax,1
 je found
 cmp eax,2
 je found
 mov eax,esi
 sub eax,[esp+4]
 cmp eax,250
 jb pause
 mov eax,[esp+16]
 cmp eax,8
 je interval_menu
 cmp eax,7
 je stop_measuring
 cmp eax,3
 je found
 cmp eax,4
 je startup
 cmp eax,5
 je status_menu
 cmp eax,6
 je passive
 # Any received but incomplete/unrecognised menu must finish. No blind I/M.
 mov eax,[ebx+0x58]
 test eax,eax
 jz no_text
 cmp dword ptr [eax-4],0
 jne pause
no_text:
 mov eax,esi
 sub eax,[esp+12]
 cmp dword ptr [esp+8],0
 jne after_initial
 cmp eax,1100
 jb pause
 lea edx,[edi+RVA+(command_g-probe)]
 mov dword ptr [esp+8],1
 jmp transmit
after_initial:
 cmp dword ptr [esp+8],1
 jne waking
 cmp eax,1100
 jb pause
 mov dword ptr [esp+8],2
 jmp send_i
waking:
 cmp dword ptr [esp+8],2
 jne pause
 mov eax,esi
 sub eax,[esp]
 cmp eax,10000
 jae failure
 mov eax,esi
 sub eax,[esp+12]
 cmp eax,50
 jb pause
send_i:
 lea edx,[edi+RVA+(command_i-probe)]
 jmp transmit
stop_measuring:
 cmp dword ptr [esp+8],5
 je pause
 mov dword ptr [esp+8],5
 jmp send_i
interval_menu:
 lea edx,[edi+RVA+(command_g-probe)]
 mov dword ptr [esp+8],6
 jmp transmit
startup:
 lea edx,[edi+RVA+(command_s-probe)]
 mov dword ptr [esp+8],3
 jmp transmit
status_menu:
 lea edx,[edi+RVA+(command_m-probe)]
 mov dword ptr [esp+8],4
 jmp transmit
passive:
 mov dword ptr [esp+8],2
 jmp send_i
transmit:
 push edx
 lea eax,[ebx+0x58]
 original 0x3f98
 pop edx
 mov eax,[ebx+0x64]
 original 0x7ffc4
 call dword ptr [edi+0x1c93f4]
 mov [esp+12],eax
 # last RX is updated only on reception, not on transmitted wake characters.
pause:
 push 5
 call dword ptr [edi+0x1c9358]
 jmp loop
found:
 lea eax,[ebx+0x5c]
 mov edx,[ebx+0x58]
 original 0x3fec
 mov eax,[ebx+0x64]
 mov edx,[eax+0x30]
 mov [ebx+0x6c],edx
 mov dl,[eax+0x4c]
 mov [ebx+0x70],dl
 mov byte ptr [ebx+0x62],1
 mov byte ptr [ebx+0x71],2
 mov byte ptr [ebx+0x60],0
 jmp done
failure:
 mov eax,[ebx+0x64]
 original 0x7f9c4
 mov byte ptr [ebx+0x61],0
 mov dword ptr [ebx+0x48],0
 mov dword ptr [ebx+0x4c],0
 jmp done
cancelled:
 mov byte ptr [ebx+0x60],0
done:
 add esp,24
 pop edi
 pop esi
 pop ebx
 ret
# EDX = NUL-terminated accumulated response, EDI = image base.
# 1 OSU107, 2 Surface, 3 main, 4 startup, 5 status, 6 passive, 7 measuring.
classify:
 push ecx
 push edx
 push esi
 test edx,edx
 jz unknown
 contains osu_banner
 test eax,eax
 jnz osu
 contains surface_banner
 test eax,eax
 jnz surface
 contains main_start
 test eax,eax
 jz check_startup
 contains main_exit
 test eax,eax
 jz unknown
 contains key_h
 test eax,eax
 jz unknown
 mov eax,3
 jmp classified
check_startup:
 contains startup_name
 test eax,eax
 jz check_status
 contains startup_end
 test eax,eax
 jnz first_menu_ready
 contains stop_end
 test eax,eax
 jz unknown
first_menu_ready:
 mov eax,4
 jmp classified
check_status:
 contains interval
 test eax,eax
 jz regular_status
 contains current_setup
 test eax,eax
 jz unknown
 contains interval_prompt
 test eax,eax
 jz unknown
 mov eax,8
 jmp classified
regular_status:
 contains coefficients
 test eax,eax
 jnz unknown
 contains interval
 test eax,eax
 jnz unknown
 contains key_m
 test eax,eax
 jz check_passive
 contains key_i
 test eax,eax
 jz check_passive
 contains start_word
 test eax,eax
 jz check_passive
 mov eax,5
 jmp classified
check_passive:
 contains passive_word
 test eax,eax
 jnz passive_yes
 contains wake_word
 test eax,eax
 jnz passive_yes
 # Known measurement rows require stopping before menu navigation.
 contains measure_t
 test eax,eax
 jz unknown
 contains measure_p
 test eax,eax
 jz unknown
 mov esi,edx
scan_n:
 mov al,[esi]
 test al,al
 jz unknown
 or al,0x20
 cmp al,'n'
 jne next_n
 mov al,[esi+1]
 cmp al,'0'
 jb next_n
 cmp al,'9'
 jbe running_yes
next_n:
 inc esi
 jmp scan_n
running_yes:
 mov eax,7
 jmp classified
passive_yes:
 mov eax,6
 jmp classified
osu:
 mov eax,1
 jmp classified
surface:
 mov eax,2
 jmp classified
unknown:
 xor eax,eax
classified:
 pop esi
 pop edx
 pop ecx
 ret
# Case-insensitive substring, preserves input registers except EAX.
substring:
 push ebx
 push ecx
 push edx
 push esi
 mov esi,edx
scan:
 cmp byte ptr [esi],0
 je absent
 xor ebx,ebx
compare:
 mov al,[ecx+ebx]
 test al,al
 jz present
 mov dl,[esi+ebx]
 test dl,dl
 jz absent
 or dl,0x20
 cmp al,dl
 jne advance
 inc ebx
 jmp compare
advance:
 inc esi
 jmp scan
present:
 mov eax,1
 jmp substring_done
absent:
 xor eax,eax
substring_done:
 pop esi
 pop edx
 pop ecx
 pop ebx
 ret
osu_banner: .asciz "osu107 instrument logger"
surface_banner: .asciz "saiv110 surface logger"
main_start: .asciz "start via key-board"
main_exit: .asciz "exit (passive)"
startup_name: .asciz "status/start/menu"
startup_end: .asciz "measurement will start in 10 sec."
stop_end: .asciz "instrument will go passive in 10 sec."
coefficients: .asciz "set coefficients"
interval: .asciz "measuring interval"
key_h: .asciz "<h>"
key_m: .asciz "<m>"
key_i: .asciz "<i>"
start_word: .asciz "start"
passive_word: .asciz "- passive -"
wake_word: .asciz "hold <i> to activate"
current_setup: .asciz "current set up:"
interval_prompt: .asciz "change: y/n menu: <g>"
measure_t: .asciz " t"
measure_p: .asciz " p"
.balign 4
.long -1,1
command_g: .asciz "G"
.balign 4
.long -1,1
command_i: .asciz "I"
.balign 4
.long -1,1
command_s: .asciz "S"
.balign 4
.long -1,1
command_m: .asciz "M"
