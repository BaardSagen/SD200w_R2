.intel_syntax noprefix
.code32
.text
.global start, timer_callback, scheduled, main_form
.set RVA, 0x23e000
.macro image_base
    call 991f
991: pop edi
    sub edi, RVA + (991b - start)
.endm
start:
    # Hook the end of FormActivate, after its initialization and cleanup.
    pushfd
    pushad
    image_base
    cmp byte ptr [edi + RVA + (scheduled-start)], 0
    jne done
    mov eax, dword ptr [ebp-4]
    cmp byte ptr [eax+0x900], 0
    jne done
    mov dword ptr [edi + RVA + (main_form-start)], eax
    mov byte ptr [edi + RVA + (scheduled-start)], 1
    lea eax, [edi + RVA + (timer_callback-start)]
    push eax
    push 100
    push 0
    push 0
    call dword ptr [edi + 0x1c9708] # SetTimer(NULL, 0, 100, callback)
    test eax, eax
    jnz done
    mov byte ptr [edi + RVA + (scheduled-start)], 0
done:
    popad
    popfd
    # Replay the five replaced epilogue bytes.
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    .byte 0xe9
    .long 0x1a4c56 - RVA - (. - start) - 4

timer_callback:
    push ebp
    mov ebp, esp
    push ebx
    push esi
    push edi
    image_base
    push dword ptr [ebp+16] # Timer ID, third stdcall argument.
    push 0
    call dword ptr [edi+0x1c97c4] # KillTimer before any UI code can reenter.
    cmp byte ptr [edi + RVA + (scheduled-start)], 1
    jne callback_done
    mov byte ptr [edi + RVA + (scheduled-start)], 2
    mov eax, dword ptr [edi + RVA + (main_form-start)]
    cmp eax, dword ptr [edi+0x1c8964] # Still the live main form.
    jne callback_done
    test eax, eax
    jz callback_done
    xor edx, edx
    # Call the original Instrument button handler, including its UI refresh.
    .byte 0xe8
    .long 0x1a0ff0 - RVA - (. - start) - 4
callback_done:
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret 16
scheduled: .byte 0
.balign 4
main_form: .long 0
