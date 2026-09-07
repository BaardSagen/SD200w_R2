# Companion application integration, 2026-09-07

Reviewed the eight HANDOVER documents dated July 9 through September 3.
The September 3 FINAL ACCEPTANCE section supersedes its earlier recovery and
artifact instructions. Firmware release/flashing work belongs to the firmware
repository; this change updates SAIV Instrument Studio.

Already implemented: Storage/Sensors status, streamed clock echo, passive
recognition, Q clock synchronization, configurable ADC/tilt presentation,
Surface naming and USB DTR information, compact+DT defaults, sensor preheat,
immediate compact startup TIME fields, historical TIMEBASE import, disk ownership
checks, and U apply acknowledgements.

Implemented here:

- Full/live `nan` tokens reserve their sensor slot and overwrite earlier values
  with missing data. Configured ADC/tilt prefixes and unit suffixes work; compact
  DATE/TIME and later sensor columns remain aligned.
- Instrument settings expose automatic Mag-Key air pressure. The canonical
  `enableAirPressureMeasurement=on/off` key defaults on, preserves explicit off,
  and uses the existing disk-write/U-apply workflow. Older firmware without the
  key does not receive it. Disk probes on all four desktop/mobile disk platforms
  carry the setting to the shared UI.
- The post-pressure S fallback requires an application-owned operation, avoiding
  unsolicited commands when firmware performs a Mag-Key pressure transaction.
- O/Z calibration on firmware O and newer waits for automatic disk/CDC recovery
  before rereading configuration. Tilt no longer queues a second USB refresh.
  Older firmware retains its previous path.
- The UI explains the in-air start requirement and final 5-10 second Mag-Key
  restart guidance. Firmware retains ownership of its I/A/A/R/S/I sequence,
  one-second quiet intervals, range handling, UART recovery and session policy.

Validation: Windows Release build and CTest core/series loader suites. Regression
coverage includes configured/unconfigured live and stored sensor failures,
all-failed rows, unit suffixes, prefixes containing `nan`, missing/default and
explicit pressure settings, preservation of unrelated keys, and Surface-only
updates. Existing immediate compact and legacy TIMEBASE tests remain enabled.

No hardware commands or flashing were performed. Physical O/Z reconnect and
Mag-Key coexistence require validation with the attached instrument; other
platform probes were updated but only Windows was compiled in this workspace.
