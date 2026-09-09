.intel_syntax noprefix
.text
.global _sit_native_call
# cdecl uintptr_t call(fn,eax,edx,ecx,stack_words,count)
_sit_native_call:
 push ebp
 mov ebp,esp
 push ebx
 push esi
 push edi
 mov ecx,[ebp+28]
 mov esi,[ebp+24]
 test ecx,ecx
 jz 2f
1: dec ecx
 push dword ptr [esi+ecx*4]
 test ecx,ecx
 jnz 1b
2: mov eax,[ebp+12]
 mov edx,[ebp+16]
 mov ecx,[ebp+20]
 call dword ptr [ebp+8]
 lea esp,[ebp-12]
 pop edi
 pop esi
 pop ebx
 pop ebp
 ret
