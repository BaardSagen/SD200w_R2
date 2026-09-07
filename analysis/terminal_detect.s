.intel_syntax noprefix
.code32
.text
.global entry, modal_bridge, direct, setup_focus
.set RVA, 0x23f000
.macro base
 call 991f
991: pop edi
 sub edi, RVA+(991b-entry)
.endm
.macro call_original rva
 .byte 0xe8
 .long \rva-RVA-(.-entry)-4
.endm
entry:
 push edi
 base
 mov byte ptr [edi+RVA+(direct-entry)],1
 pop edi
 .byte 0xe9
 .long 0x1a109c-RVA-(.-entry)-4

modal_bridge:
 push edi
 base
 cmp byte ptr [edi+RVA+(direct-entry)],0
 jne detect
 pop edi
 jmp dword ptr [edx+0xd8] # Unchanged Setup ShowModal.
detect:
 mov byte ptr [edi+RVA+(direct-entry)],0
 push ebx
 mov ebx,eax
 xor edx,edx
 call_original 0x1131bc # Setup.FormShow: initialize controls from current settings.
 mov eax,ebx
 mov edx,dword ptr [ebx+0x2d8]
 call_original 0x116224 # Original DetectBtnClick.
 mov eax,dword ptr [edi+0x1b1e1c]
 mov eax,dword ptr [eax]
 cmp dword ptr [eax+0x234],1 # Only apply after accepting the detection dialog.
 jne cancelled
 mov eax,ebx
 mov edx,dword ptr [ebx+0x2d0]
 call_original 0x113c0c # Setup.OKBtnClick: store detected settings as usual.
 mov eax,1 # Existing main Setup handler applies and refreshes communication.
 jmp finish
cancelled:
 mov eax,2
finish:
 pop ebx
 pop edi
 ret
setup_focus:
 cmp byte ptr [ebx+0x47],0 # Hidden Setup initialization cannot focus its OK button.
 je no_focus
 jmp dword ptr [edx+0xb0]
no_focus:
 ret
direct: .byte 0
