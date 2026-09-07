.intel_syntax noprefix
.code32
.text
.global guard_start, receive_hook, click_hook, after_modal_hook, close_port_hook
.global matcher, blocked, requested, pending, pattern, prefix, message
.set GUARD_RVA, 0x285000

# Every reference is relative to the runtime image base, including after rebasing.
.macro image_base
    call 991f
991: pop edi
    sub edi, GUARD_RVA + (991b - guard_start)
.endm
.macro original_jump rva
    .byte 0xe9
    .long \rva - GUARD_RVA - (. - guard_start) - 4
.endm
.macro state reg, symbol
    lea \reg, [edi + GUARD_RVA + (\symbol - guard_start)]
.endm

guard_start:
receive_hook:
    # Replaced instructions at 0x59b308. BL is the instrument byte.
    mov bl, byte ptr [eax + edx - 1]
    pushfd
    pushad
    image_base
    movzx eax, bl
    call feed_byte
    test eax, eax
    jz receive_done
    state ecx, blocked
    mov byte ptr [ecx], 1
    state ecx, requested
    cmp byte ptr [ecx], 1
    jne receive_done
    mov esi, dword ptr [edi + 0x1b21e0]
    mov esi, dword ptr [esi]
    test esi, esi
    jz receive_done
    cmp byte ptr [esi + 0xa60], 0 # Leave the separate Log operation alone.
    jne receive_done
    cmp byte ptr [esi + 0xa61], 0
    je receive_done
    state ecx, pending
    mov byte ptr [ecx], 1
    # Same cancellation/error flags as the existing unsupported-response path.
    mov byte ptr [esi + 0xa61], 0
    mov byte ptr [esi + 0xa62], 1
    mov byte ptr [esi + 0xa63], 1
    mov dword ptr [esi + 0x234], 2 # mrCancel: unwind ShowModal normally.
    mov eax, dword ptr [edi + 0x1b22a4]
    mov byte ptr [eax], 0
    mov eax, dword ptr [esi + 0x3fc]
    xor edx, edx
    lea ecx, [edi + 0x61250] # TTimer.SetEnabled(False).
    call ecx
receive_done:
    popad
    popfd
    mov eax, ebx
    original_jump 0x19b30e

click_hook:
    pushfd
    pushad
    image_base
    state ecx, requested
    mov byte ptr [ecx], 0
    cmp edx, dword ptr [eax + 0x374] # Sender = btnDownload.
    jne click_continue
    state ecx, matcher
    mov byte ptr [ecx], 0
    state ecx, pending
    mov byte ptr [ecx], 0
    state ecx, requested
    mov byte ptr [ecx], 1
click_continue:
    popad
    popfd
    push ebx
    push esi
    mov esi, edx
    mov ebx, eax
    original_jump 0x1a14fa
click_block:
    call show_message
    popad
    popfd
    ret

after_modal_hook:
    pushfd
    pushad
    image_base
    state ecx, requested
    mov byte ptr [ecx], 0
    state ecx, pending
    cmp byte ptr [ecx], 0
    je modal_normal
    mov byte ptr [ecx], 0
    mov eax, dword ptr [edi + 0x1b2174]
    mov eax, dword ptr [eax]
    mov eax, dword ptr [eax + 0x510]
    state edx, yes_command
    lea ecx, [edi + 0x7ffc4] # Existing serial string write, also used for F.
    call ecx
    call show_message
    popad
    popfd
    # Do not send the original ESC or start post-download processing.
    original_jump 0x1a15c7
modal_normal:
    popad
    popfd
    cmp eax, 2
    jne modal_not_cancelled
    original_jump 0x1a1574
modal_not_cancelled:
    original_jump 0x1a1586

close_port_hook:
    pushfd
    pushad
    image_base
    mov ecx, dword ptr [edi + 0x1b2174]
    mov ecx, dword ptr [ecx]
    test ecx, ecx
    jz close_done
    cmp eax, dword ptr [ecx + 0x510]
    jne close_done
    state ecx, blocked
    mov byte ptr [ecx], 0
    state ecx, matcher
    mov byte ptr [ecx], 0
close_done:
    popad
    popfd
    push ebp
    mov ebp, esp
    xor ecx, ecx
    original_jump 0x7f9c9

# KMP stream matcher: ASCII case-insensitive, ignores whitespace, survives chunks.
# EDI is image base; AL is input byte; EAX returns 1 only at a complete match.
feed_byte:
    cmp al, 32
    je no_match
    cmp al, 9
    je no_match
    cmp al, 10
    je no_match
    cmp al, 13
    je no_match
    cmp al, 'A'
    jb folded
    cmp al, 'Z'
    ja folded
    add al, 32
folded:
    state edx, matcher
    movzx ecx, byte ptr [edx]
    state ebx, pattern
match_retry:
    cmp al, byte ptr [ebx + ecx]
    je char_match
    test ecx, ecx
    jz save_matcher
    state esi, prefix
    movzx ecx, byte ptr [esi + ecx - 1]
    jmp match_retry
char_match:
    inc ecx
    cmp ecx, pattern_end - pattern
    jne save_matcher
    mov byte ptr [edx], 0
    mov eax, 1
    ret
save_matcher:
    mov byte ptr [edx], cl
no_match:
    xor eax, eax
    ret

show_message:
    state eax, user32_name
    push eax
    call dword ptr [edi + 0x1c9224]
    test eax,eax
    jz message_done
    state edx, timeout_name
    push edx
    push eax
    call dword ptr [edi + 0x1c9220]
    test eax,eax
    jz message_done
    push 3000
    push 0
    push 0x2040
    state edx, title
    push edx
    state edx, message
    push edx
    push 0
    call eax # MessageBoxTimeoutA: automatically closes after 3000 ms.
message_done:
    ret

.balign 4
.long -1,1
yes_command: .asciz "Y"
user32_name: .asciz "user32.dll"
timeout_name: .asciz "MessageBoxTimeoutA"

pattern: .ascii "refreshdisky/n"
pattern_end:
prefix: .byte 0,0,0,1,2,0,0,0,0,0,0,0,0,0,0
message: .asciz "Preforming refresh off disks"
title: .asciz "MiniSoft SD200W"
matcher: .byte 0
blocked: .byte 0
requested: .byte 0
pending: .byte 0
