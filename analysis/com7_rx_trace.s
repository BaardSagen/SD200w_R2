.intel_syntax noprefix
.code32
.text
trace_start:
push dword ptr [esp+20]
push dword ptr [esp+20]
push dword ptr [esp+20]
push dword ptr [esp+20]
push dword ptr [esp+20]
.byte 0xe8
.long 0x7b4c-2736128-(.-trace_start)-4
pushad
mov edx,[esp+48]
cmp dword ptr [edx],0
jne record
cmp dword ptr [esp+28],0
jne done
record:
call loc
loc: pop edi
sub edi,2736128+(loc-trace_start)
mov ebx,[edi+2740224]
cmp ebx,500
jae done
imul esi,ebx,32
lea esi,[edi+esi+2740228]
inc ebx
mov [edi+2740224],ebx
call dword ptr [edi+0x1c93f4]
mov [esi],eax
mov eax,[esp+36]
mov [esi+4],eax
mov eax,[esp+48]
mov eax,[eax]
mov [esi+8],eax
mov eax,[esp+28]
mov [esi+12],eax
mov edx,[esp+40]
mov eax,[edx]
mov [esi+16],eax
mov eax,[edx+4]
mov [esi+20],eax
mov eax,[edx+8]
mov [esi+24],eax
mov eax,[edx+12]
mov [esi+28],eax
done: popad
ret 20
