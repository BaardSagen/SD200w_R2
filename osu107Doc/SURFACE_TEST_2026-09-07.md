# Surface Logger acceptance, COM11

Observed SAIV110 Surface logger SN107, firmware 0.9.9Q, stopped, LT.
The mounted system.ini has surface.enable=1 and instrument0.enable=0.
Initial system.ini SHA256:
F49B7C13304E95007D4037845A6353BD9835309859020E3EE62D7772F1E10BF0.

## Passed on hardware

- Read-only USB identification: first identity after 0.125 seconds, TX=0.
- C++ preferred-port probe: identity in approximately 0.37 seconds, TX=0.
- Actual application-state acceptance: Connected immediately; no CTD awake
  state and no Connect wake job.
- Actual X clock action: device confirmed
  `OK: logger clock 2026-09-07 17:35:33 LT`, then returned to
  `SAIV110 surface-logger Menu:` with `Surface-logger: Stopped`.
  No CTD wake command was sent.

## Findings fixed

- Start/Stop and state-query eligibility now use the live Surface identity;
  they no longer require an earlier mounted-disk scan.
- The parser accepts the observed `OK: logger clock ... LT|GMT` confirmation
  so the logger's confirmed timestamp can populate the clock panel.
- Live test capture accumulates fragmented greetings instead of treating an
  initial blank line as the entire status response.

## Pending

Immediate reopen after the X test returned only a blank line. The next
independent serial open was denied access. Another process was found running
`python -u -i tmp/local_clock_console.py` (PID 2056); it was not terminated.
The operator was asked to free COM11. Our test process closed its handle.

### Completed after the port was released

- A 750 ms gap between closing and reopening CDC allowed the device to observe
  DTR low and produce a fresh greeting. Immediate reopening had reproduced
  a blank greeting even after the competing port use ended.
- The clock was set to `26-09-07-17-43-22 LT`; fresh USB status returned
  `2026-09-07 17:43:23 (LT)`. No CTD wake job was started.
- U initially exposed an application bug: the read ended at a pause between
  MIR and APPLY. The application now waits for the explicit final
  `OK SAIV110_UPDATE_CONFIG` (or failure) instead of an idle window or
  intermediate staged/APPLY OK. The actual application U action then passed.
- Firmware reported no changes versus staged config/NVS. SHA256 comparison of
  the mounted config INI files before and after the initial U check found no
  differences. No config file or calibration was edited.
- Actual application Start/Stop actions passed. During the 12-second capture:
  `S1 17:43:28 Par4.26 OxR0.29 Tilt=1` and
  `S2 17:43:33 Par4.26 OxR0.29 Tilt=1` were received. Stopped was confirmed
  before ending the test. No CTD awake/stream state was created.
- Windows build and all three CTest suites passed after the fix.
- Main GUI startup at 17:43:55 detected Surface at 17:43:56 with TX=0 and
  remained responsive.
- Physical USB unplug/replug passed: GUI observed COM11 disappear at 17:45:04,
  reopened it at 17:45:07, and received Surface identity and Stopped at
  17:45:08. No serial TX entries were recorded. GUI remained responsive.
- The GUI was closed normally after acceptance; a final open/close with DTR
  disabled verified COM11 was available. No serial bytes were sent by that check.

The logging test created new Surface measurement data. Firmware reports that
F disk refresh is needed to see the latest files; this test has not yet
validated the new files through mounted storage.

Evidence: `live_test_artifacts/surface_initial_20260907.json` and the runtime
log under `live_test_artifacts/usb_discovery_test_files/progLog/` from 17:35.
