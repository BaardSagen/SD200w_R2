# USB autodetection and wake separation, 2026-09-07

The Windows application now opens serial with DTR enabled after receive setup,
preserving the USB-open greeting instead of purging it. Discovery listens up to
900 ms for a complete OSU107/SAIV110 identity before using the existing legacy
probe. Fragmented identity text is accumulated within that bounded window.

A current logger is identified without I, M, S or Ctrl+T. The result does not
claim an awake CTD or a missing CTD. OSU107 retains the **Connect instrument**
button; only an explicit connect/measurement request starts its wake workflow.
Surface Logger becomes ready directly, with its running/stopped state taken
from USB status and S rows. Current USB identity overrides cached disk mode.

USB discovery does not wait for a filesystem scan. The firmware can expose CDC
with MSC unavailable; disk/configuration access remains available through the
normal Data via Disk/Rescan actions. This also avoids a startup UI stall observed
when immediately probing the logger filesystem.

Port arrival/disappearance is checked each second. An existing connection is
reopened without the former Ctrl+T/backspace/M/Q identity probe. New ports also
trigger discovery when the application is offline. Older instruments without
a USB logger greeting retain the existing active discovery/wake fallback.

## Verification

- User specified COM7; enumeration instead found COM11, USB serial
  `OSU107-SN0107`, firmware `0.9.9P`. Tests used this observed unit.
- Three read-only opens received the complete identity after approximately
  0.17-0.20 s, with zero serial bytes transmitted.
- The actual C++ preferred-port probe completed in approximately 0.48 s and
  recorded `USB identity COM11 TX=0`.
- An isolated copy of the GUI completed startup detection without serial
  commands. The earlier synchronous-disk version stalled; after separating
  discovery from disk access, the GUI remained responsive and closed normally.
- A separate explicit wake-only smoke test sent the legacy wake sequence and
  reached the attached instrument's main menu. No measurement, configuration,
  pressure adjustment, erase or firmware update operation was requested.
- H was sent after the complete main menu and a one-second quiet interval;
  `- passive -` and the wake prompt were received. A subsequent read-only open
  again reported `Hold <I> to wake instrument`.
- Regression tests cover complete/fragmented USB identity, CR/LF forms, metadata,
  legacy CTD exclusion, Surface readiness, S-row state, stale disk-mode data,
  the Connect instrument label, and real CTD measurement recognition.

Physical Surface Logger acceptance is pending. Surface behavior has been tested through the actual app
state machine with synthetic terminal input, not on physical Surface hardware.

### Operator USB replug test

The operator unplugged and reinserted USB on COM11 / `OSU107-SN0107`.
The read-only monitor observed disappearance and return of the same USB serial.
The initial identity took 0.25 s after port open; after replug it took 0.609 s.
Both captures transmitted zero serial bytes and reported
`Hold <I> to wake instrument`. This passes physical USB status discovery;
GUI reconnect and physical Surface mode remain separate acceptance checks.
Capture: `live_test_artifacts/usb_replug_instrument_operator_20260907.json`.

The operator repeated unplug/replug with the GUI running. Its log recorded
COM11 disappearing at 12:02:17, reopening at 12:02:26, and receiving the USB
identity and `Hold <I> to wake instrument` at 12:02:27. No serial TX entries
were present. The GUI remained responsive. This verifies GUI transport recovery
and passive receipt.

### Actual Connect action on COM11

The live application-state harness (`sd200w_usb_discovery_state_tests
--live-connect COM11`) invokes the same `connectInstrument()` action as the
GUI button. It first exposed a failure: the quick current-link check sent only
five isolated I commands and reported no instrument while the CTD slept.
Known sleeping connections now use the existing full wake sequence, with
passive context replacing the USB greeting before probing. Automatic USB
discovery still sends no commands.

After rebuilding, the live test passed: passive identity kept `instrumentAwake`
false and the button at `Connect instrument`; the explicit action reached
`Awake in main menu`, set awake true, and changed the button to `Connected`.
The test then sent H and received `- passive -`. Total test time was about
9.5 seconds. Air pressure adjustment was disabled for this connection test.
This validates the application action and state, not a desktop mouse click.

## Prepared read-only physical test

Close other programs using the logger port, then run from the repository root:

```powershell
python tests/usb_logger_status_check.py --usb-serial OSU107-SN0107 --expected instrument --repeat 3 --watch-replug --output live_test_artifacts/usb_replug_instrument.json
```

After each `READY`, unplug USB and reconnect it. The script tracks the USB
serial rather than a fixed COM number. It never sends serial commands, and
records timing and received text. Repeat with `--expected surface` after the
operator selects Surface Logger mode. Separately repeat unplug/replug with the
GUI running and verify the button/state without pressing Connect instrument.

The GUI and script must not own the same COM port at the same time.
