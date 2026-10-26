.intel_syntax noprefix
.code32
.text
.global entry, import_entry, import_file, import_title, import_filter
.global capture, selected, download, prescan, logger_line
.global ascii_mode, confirmed_type, confirmed_port, pending_type, pending_port, logger_active
.macro base
 call 991f
991: pop edi
 sub edi, RVA+(991b-entry)
.endm
.macro jump target
 .byte 0xe9
 .long \target-RVA-(.-entry)-4
.endm
.macro invoke target
 .byte 0xe8
 .long \target-RVA-(.-entry)-4
.endm
entry:
import_entry:
 pushfd
 pushad
 base
 mov byte ptr [edi+RVA+ascii_mode-entry],0
 test edx,edx
 jz import_entry_done
 cmp dword ptr [edx+0xc],0x41534349
 jne import_entry_done
 mov byte ptr [edi+RVA+ascii_mode-entry],1
import_entry_done:
 popad
 popfd
 jump OLD_IMPORT_ENTRY
import_file:
 pushfd
 push edi
 base
 cmp byte ptr [edi+RVA+ascii_mode-entry],1
 pop edi
 je ascii_file
 popfd
 jump OLD_IMPORT_FILE
ascii_file:
 popfd
 lea edx,[ebp-0x20]
 mov eax,[ebx+0x2e8]
 jump 0x1a5a53
import_title:
 pushfd
 push edi
 base
 lea edx,[edi+RVA+convert_title-entry]
 cmp byte ptr [edi+RVA+ascii_mode-entry],1
 jne title_done
 lea edx,[edi+RVA+ascii_title-entry]
title_done:
 pop edi
 popfd
 jump 0x1a596c
import_filter:
 push edi
 base
 lea edx,[edi+RVA+convert_filter-entry]
 cmp byte ptr [edi+RVA+ascii_mode-entry],1
 jne filter_done
 lea edx,[edi+RVA+ascii_filter-entry]
filter_done:
 pop edi
 jump 0x1a5998

# Worker identities must be copied before the original FormClose frees workers.
capture:
 pushfd
 pushad
 base
 mov byte ptr [edi+RVA+pending_type-entry],0
 mov byte ptr [edi+RVA+pending_port-entry],0
 mov esi,[eax+0x330]
 test esi,esi
 jz capture_done
 mov ebx,[esi-4]
 test ebx,ebx
 jle capture_done
capture_row:
 mov eax,[esi+16]
 test eax,eax
 jz capture_next
 cmp dword ptr [eax-4],5
 jne capture_next
 cmp dword ptr [eax],0x74736e49
 jne capture_next
 cmp byte ptr [eax+4],'r'
 jne capture_next
 mov eax,[esi]
 test eax,eax
 jz capture_done
 cmp byte ptr [eax+0x60],0
 jne capture_done
 cmp byte ptr [eax+0x62],1
 jne capture_done
 cmp byte ptr [eax+0x71],2
 jne capture_done
 mov ecx,[eax+0x64]
 test ecx,ecx
 jz capture_done
 mov cl,[ecx+0x34]
 mov [edi+RVA+pending_port-entry],cl
 mov edx,[eax+0x5c]
 invoke CLASSIFY
 cmp eax,1
 je capture_logger
 cmp eax,2
 jne capture_done
capture_logger:
 mov [edi+RVA+pending_type-entry],al
 jmp capture_done
capture_next:
 add esi,20
 dec ebx
 jnz capture_row
capture_done:
 popad
 popfd
 jump OLD_CAPTURE
selected:
 invoke OLD_SELECTED
 pushfd
 pushad
 base
 cmp eax,1
 jne selected_done
 mov byte ptr [edi+LOGGER_KNOWN],0
 mov al,[edi+RVA+pending_type-entry]
 mov [edi+RVA+confirmed_type-entry],al
 mov al,[edi+RVA+pending_port-entry]
 mov [edi+RVA+confirmed_port-entry],al
selected_done:
 popad
 popfd
 ret

download:
 pushfd
 pushad
 base
 mov byte ptr [edi+RVA+logger_active-entry],0
 cmp edx,[eax+0x374]
 jne download_done
 mov esi,[eax+0x510]
 test esi,esi
 jz download_done
 cmp byte ptr [esi+0x407e],0
 jne download_done
 cmp byte ptr [edi+LOGGER_KNOWN],1
 je use_logger
 cmp byte ptr [edi+RVA+confirmed_type-entry],0
 je download_done
 mov dl,[edi+RVA+confirmed_port-entry]
 test dl,dl
 jz download_done
 cmp dl,[esi+0x34]
 jne download_done
use_logger:
 mov byte ptr [edi+RVA+logger_active-entry],1
 mov byte ptr [edi+LOGGER_KNOWN],1
download_done:
 popad
 popfd
 jump OLD_DOWNLOAD

# For a known logger, do not scan stale terminal history for CTD/Burst headers.
prescan:
 pushfd
 push edi
 base
 cmp byte ptr [edi+RVA+logger_active-entry],1
 pop edi
 jne prescan_native
 popfd
 mov byte ptr [eax+0xa67],0
 ret
prescan_native:
 popfd
 push ebp
 mov ebp,esp
 mov ecx,0x11
 jump 0x1518ec

# Bytes still reach the existing refresh/reply state machine. Logger response
# lines must not enter the CTD measurement parser during this Download.
logger_line:
 pushfd
 push edi
 base
 cmp byte ptr [edi+RVA+logger_active-entry],1
 jne line_native
 cmp byte ptr [edi+REQUESTED],1
 jne line_native
 cmp byte ptr [eax+0xa60],0
 jne line_native
 pop edi
 popfd
 ret
line_native:
 pop edi
 popfd
 jump OLD_LINE

.balign 4
ascii_mode: .byte 0
confirmed_type: .byte 0
confirmed_port: .byte 0
pending_type: .byte 0
pending_port: .byte 0
logger_active: .byte 0
.balign 4
.long -1,15
convert_title: .asciz "Convert CSV/TXT"
.balign 4
.long -1,14
ascii_title: .asciz "Import CSV/TXT"
.balign 4
.long -1,convert_filter_end-convert_filter-1
convert_filter: .asciz "CSV/TXT files (*.csv;*.txt)|*.csv;*.txt|Burst Files (*.burst)|*.burst|All files (*.*)|*.*"
convert_filter_end:
.balign 4
.long -1,ascii_filter_end-ascii_filter-1
ascii_filter: .asciz "Instrument text (*.csv;*.txt)|*.csv;*.txt|Burst Files (*.burst)|*.burst|All files (*.*)|*.*"
ascii_filter_end:
