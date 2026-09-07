# Application integration of the September 7 Q handovers

Reviewed LOCAL_CLOCK, HIDDEN_UPDATE_CONFIG and NUMERIC_MENU_ECHO, including
the final Q release and mutually exclusive logger modes.

## Changes

- Firmware Q and later exposes local PC-to-logger clock setting via X in both
  Instrument and Surface modes. LT/GMT selection determines the transmitted
  time; the subsequent Y/N response only changes the device's timezone label.
  The target is generated after the format prompt, and pasted input is used
  only for this new local dialog. No automatic G follows successful completion.
- CTD-to-OSU synchronization remains a separate Q action. The combined CTD
  clock setup still invokes this synchronization after setting the CTD; it
  does not silently switch to independent PC-to-logger setting on Q firmware.
- Local dialog reads accumulate fragmented prompts and stop at a bounded
  deadline. If X is rejected, no value or escape is sent into an unknown
  instrument submenu. Failed entry after a confirmed local format prompt uses
  G for Instrument mode or Esc for Surface. Failures acknowledge that Enter
  may already have changed time. Successful writes are not presented as an
  independent clock readback; a new status observation is needed.
- Q passive U goes directly to the local configuration action without a CTD
  wake/menu probe. Logging blocks both local clock setting and config apply.
  Existing disk-refresh and firmware error handling remain in effect.
- Manual CLI input disarms automatic keep-alive G/N until a received main-menu
  end marker re-arms it. This accommodates long numeric fields and self-test.
  Existing CLI partial-line rendering already displays unterminated echo and
  progress; automatic CTD calibration entry remains paced.
- Firmware P and older retain their existing clock and U paths. Some interim
  firmware handovers used P with new features, but the application enables them
  at the final published Q version rather than guessing from P's version string.

The existing mode rewrite already enables one of surface/instrument0 and
disables the other. Existing round-trip tests cover both directions; legacy
configuration parsing was not made stricter than the firmware migration rule.

## Verification and limits

Windows build and all three CTest suites pass. New regression cases cover
X format/timezone prompts arriving byte by byte, LT/GMT reply selection,
rejected X, mode-specific failure cleanup, no automatic wake/navigation,
P/Q gating, logging guards, passive U routing, and partial self-test progress.

No serial port was opened, no firmware was flashed, and no device configuration
or calibration was changed during this integration. Q hardware acceptance of
X/U and visual checks of the clock panel remain to be performed. The previously
measured CTD PC-time entry delay is not corrected by this change; X sets only
the logger clock independently.
