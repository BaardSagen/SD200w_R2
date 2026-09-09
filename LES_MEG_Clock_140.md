# SAIV IT 1.4.0 - clock set once

Customer release: SAIV_Instrument_Terminal_v1.4.0_Sept2026.exe. Only this EXE is needed. Earlier releases remain available.

Version 1.3.9 could write the attached SD200 clock twice: its first timestamp aged during character-by-character transfer, then the readback triggered a compensated retry. COM11 reproduced two SD200 writes plus one OSU107 write.

Version 1.4.0 sends the date/hour prefix first, then calculates minutes and seconds immediately before sending them. The measured prefix duration estimates the remaining five characters. SD200 receives one complete timestamp and one Enter. There is no automatic second write. OSU107 still receives its separate clock setting once. Both clocks retain independent readback checks against PC time with a five-second tolerance. LT/GMT choices remain available.

If PC time changes unexpectedly, transfer takes too long, or the predicted hour differs from the already entered prefix, the operation stops before Enter and reports that Detect/retry is needed. A failed readback reports failure instead of rewriting the clock. Time entry may remain open after an interrupted operation.

Physical test of the delivered EXE: COM11, OSU107 SN107 with SD208 SN1456, GMT. Receive transcript confirms exactly one SD200 write dialog and one logger write dialog; both clock readbacks passed. Interval was not written. Reports: analysis/runtime_test/settings140/physical_gui_validation.json and clock_write_count.json. Surface was not physically tested in this change.

Validation: 932 portable protocol/config checks, 20 native gateway/ASLR checks, and actual single-EXE GUI checks. Formula/UART/refresh code is preserved. Build: analysis/build_single_exe_140.py. Previous 1.3.9 module source preserved in analysis/reference/sit_import_v139; its build uses that archive. Work remains on feature/import-all-fields, no push.
