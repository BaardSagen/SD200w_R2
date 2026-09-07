.intel_syntax noprefix
.code32
.text
.global double_click
.set RVA,0x284000
.macro original target
 .byte 0xe8
 .long \target-RVA-(.-double_click)-4
.endm
double_click:
 push ebx
 push edi
 mov ebx,eax
 mov edx,1
 mov eax,[ebx+0x2e4]
 original 0xf180c
 test eax,eax
 js done
 mov eax,ebx
 original 0x111c34
 call here
here: pop edi
 sub edi,RVA+(here-double_click)
 mov eax,[ebx+0x2d0]
 # OKBtn offset is filled by builder after validating form fields.
 push 0
 push 0
 push 0xf5
 push dword ptr [eax+0x14c]
 call dword ptr [edi+0x1c9750]
done:
 pop edi
 pop ebx
 ret
