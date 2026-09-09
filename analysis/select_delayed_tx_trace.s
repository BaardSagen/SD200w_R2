.intel_syntax noprefix
.code32
.text
trace_start:
pushad
call loc
loc: pop edi
sub edi,2744326
mov ebx,[edi+2748416]
cmp ebx,500
jae done
imul esi,ebx,16
lea esi,[edi+esi+2748420]
inc ebx
mov [edi+2748416],ebx
call dword ptr [edi+0x1c93f4]
mov [esi],eax
mov eax,[esp+36]
mov [esi+4],eax
mov eax,[esp+40]
movzx eax,byte ptr [eax]
mov [esi+8],eax
mov eax,[esp+44]
mov [esi+12],eax
done:
push dword ptr [esp+52]
push dword ptr [esp+52]
push dword ptr [esp+52]
push dword ptr [esp+52]
push dword ptr [esp+52]
.byte 0xe8
.long 0x7bec-2744320-(.-trace_start)-4
mov [esp+28],eax
cmp ebx,500
jae finished
mov edx,[esp+48]
mov edx,[edx]
shl edx,8
or eax,edx
mov [esi+12],eax
finished: popad
ret 20
