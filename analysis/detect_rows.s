.intel_syntax noprefix
.code32
.text
.global row_color
.set RVA,0x241000
row_color:
 push eax
 push ecx
 push edx
 call get_base
get_base:
 pop eax
 sub eax,RVA+(get_base-row_color)
 mov eax,[eax+0x1b1e1c]
 test eax,eax
 jz done
 mov eax,[eax]
 test eax,eax
 jz done
 cmp ebx,[eax+0x2e4]
 jne done
 mov ecx,[ebp+8]
 test ecx,ecx
 js done
 mov eax,[eax+0x330]
 test eax,eax
 jz done
 cmp ecx,[eax-4]
 jae done
 imul ecx,ecx,20
 mov eax,[eax+ecx]
 test eax,eax
 jz done
 cmp byte ptr [eax+0x60],0
 jne done
 cmp byte ptr [eax+0x71],2
 jne done
 mov dword ptr [ebp-8],0x00d8f2d8
 xor edi,edi
done:
 pop edx
 pop ecx
 pop eax
 mov edx,edi
 mov eax,[esi+0xc]
 .byte 0xe9
 .long 0xf269a-RVA-(.-row_color)-4
