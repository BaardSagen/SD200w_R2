# CTD and OSU107 clock test

Hardware: COM11, OSU107 SN107 firmware 0.9.9P with attached CTD.
Surface Logger was not tested or enabled.

The live application harness invokes Connect instrument, Set time, LT from
the PC, and the automatic OSU107 Q/Y synchronization. The CTD clock is read
through S and the verification prompt is declined with N. Pressure adjustment
is disabled. The instrument is returned to passive with H after the test.

## Fixes found by testing

- Preserve the requested follow-up OSU synchronization through both CTD flow
  initialization resets. Ordinary reset/cancellation still clears the request.
- Accept both `OSU107 option:` and the older `OSU-107 option:` menu headers.
- Wait for the delayed CTD menu following G before sending another wake command.
- Parse `(LT)` and `(GMT)` in USB Date/time status instead of displaying N/A.

## Results

`sd200w_usb_discovery_state_tests --live-clocks COM11` passed after the fixes.
CTD verification returned `Date 26-09-07`, `Time 12-15-37 LT`.
OSU subsequently confirmed:
`Date & time in OSU is now synced to CTD time date = 2026-09-07-12-15-48 LT`.
H returned the passive banner. A fresh USB open independently read OSU time
without transmitting serial bytes.

Timing limitation: the clock value is generated before the paced CTD character
entry completes. This test observed about 4–5 seconds delay at CTD readback;
the app's displayed 7-second skew also includes time waiting for the final
menu. Independent USB observation at PC 12:16:43.861 returned OSU 12:16:38 LT
(about 5.9 seconds behind, with one-second device timestamp resolution).
This validates setting and synchronization, not precise PC time alignment.
GMT switching, cancellation, and RTC retention after power removal were not
tested on hardware in this run.

All three CTest suites passed, including regression checks for synchronization
intent, current/legacy menu headers, and USB clock zones.

Artifacts: `live_test_artifacts/usb_discovery_test_files/progLog/`,
`live_test_artifacts/clock_sync_usb_readback_20260907.json`, and
`live_test_artifacts/clock_sync_offset_20260907.json`.
