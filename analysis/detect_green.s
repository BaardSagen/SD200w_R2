.intel_syntax noprefix
.code32
.text
.global refresh, reset, update_color, apply_color, green_color
.set RVA,0x240000
.macro original rva
 .byte 0xe8
 .long \rva-RVA-(.-refresh)-4
.endm
refresh:
 original 0x61250
 pushad
 mov ebx,[ebp-4]
 call update_color
 popad
 ret
reset:
 original 0xf3050
 pushad
 mov ecx,0x80000005
 call apply_color
 popad
 ret
update_color:
 mov ecx,0x80000005
 mov esi,[ebx+0x330]
 test esi,esi
 jz apply_color
 mov edi,[esi-4]
 test edi,edi
 jle apply_color
scan:
 mov eax,[esi]
 test eax,eax
 jz next
 cmp byte ptr [eax+0x60],0
 jne next
 cmp byte ptr [eax+0x71],2
 je green_color
next:
 add esi,20
 dec edi
 jnz scan
 jmp apply_color
green_color:
 mov ecx,0x00d8f2d8
apply_color:
 push ecx
 mov eax,[ebx+0x2e4]
 mov edx,1
 original 0xf1b34
 pop ecx
 mov eax,[ebx+0x2e4]
 xor edx,edx
 original 0xf1b34
 ret
