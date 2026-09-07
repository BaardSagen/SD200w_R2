# Instrument numeric-menu echo, 2026-09-07

## Problem and scope

The 0.9.9F change supplied a generic `IInstrument` framing hook but only enabled
it during the exact clock prompt `Format: YY-MM-DD-HH-MM-SS`. Oxygen SAIV205
calibration and coefficient entry still buffered echoed digits until CR/LF.

Enable immediate echo for `<C>` and `<M>` selected inside the confirmed
instrument main menu. `<M>` at the start/status prompt only opens the menu.
Keep the echo state across field terminators. Clear it on G/H/R, confirmed
main/stop menu return, passive/wake text, and measurement/header traffic.
Other numeric submenus remain outside this change pending protocol evidence.

## Implementation

- `sd204_8_instrument`: a separate numeric-menu echo state supplements clock echo.
- `instrument_rx_stream.hpp`: existing UART stream framing moved into a
  host-testable header. Track bytes already displayed while retaining the full
  line for `processIncoming`. Only the remaining display suffix is emitted.
  Parser-appended suffixes are retained when the displayed prefix matches.
  A prefix already sent to the terminal cannot be rewritten retroactively.
- `uart_runtime.cpp`: clear the display count together with stream carry on an
  RX generation change or dropped queue fragment.

## Validation

- PCB 3.1.2 incremental firmware build passed.
- `instrument_rx_stream_test.cpp` passed: every two-chunk split of a multi-field
  exchange, byte-at-a-time echo, split menu exit, return to measurement buffering,
  clock prompt, split CR/LF, oversized carry, and OSU menu suffix preservation.
- Existing `interval_logic_test.cpp` passed with `session_disk_policy.cpp` and
  `headless_sleep_policy.cpp` linked using the MinGW64 C++17 host compiler.
- COM11 identifies OSU107-SN0107 / PCB 3.1.2, installed version 0.9.9P.
  COM6 identifies J-Link serial 69650428.
- Existing firmware confirmed `<C>` -> `Oxygen calibration: Y/N` and `<M>` ->
  `Set coefficient`, first coefficient `A1+8.7419864614E-04`.
  `<G>` in coefficient selection asks `Save coefficients in back-up: Y/N`.
  This initial inspection did not enter or save a calibration value.

## Hardware verification

App-only flash completed on SN107 using J-Link 69650428; programming verification
and final system reset passed. Flash preflight confirmed no accessible OSU disk
and live COM11. MCUboot/NVS were not erased.

`V` in the local OSU menu reports:

- SW: OSU107 ver-0.9.9P
- HW: OSU-M rev-3.1.2
- Build: Sep 07 2026 13:57:41
- Git: main@602becb1 (working-tree echo changes included; not committed)

Hardware echo checks:

- `<M>` / Set coefficient / Y: `A1` appears without a line terminator.
  Sent the original `+8.7419864614E-04` character by character and verified all
  17 characters appeared before Enter, exactly once. Enter advanced to B1.
  Returned with G, declined backup saving, reopened M and confirmed unchanged A1.
- `<C>` / Oxygen calibration / Y / temperature confirmation: `OX=` appears
  without a line terminator. Sent `+0100` with 0.6 s between characters and
  verified all five characters appeared before Enter, exactly once.
  Initial test stopped without submitting a complete oxygen value; see the full
  authorized follow-up below.
- Fast multi-character transmission at the oxygen prompt returned only its
  first character; paced typing worked. This may be an instrument input-rate
  constraint and is separate from the missing pre-Enter echo addressed here.

Serial transcript: workspace `tmp/numeric_menu_after.log`.

### Authorized full-dialog follow-up

The operator explicitly authorized all testing on the instrument attached to
COM11, including changes to test calibration. The oxygen field did not exit
while the port was closed. The OSU greeting incorrectly suggested passive state;
wake-I was instead received by the still-active OX field and rejected.

Sent the complete `+0100.00000` with 0.6 s between characters. All 11 characters
were received exactly once before Enter. Enter completed the oxygen calibration
and produced `V -3.49840061755605`. Answered N to backup saving, returned to the
main menu, and confirmed the new active factor in the calibration listing.
The prior oxygen factor was not captured and has not been restored. This is a
test calibration. The partial post-test coefficient listing is saved in workspace
`tmp/numeric_coefficients_after_oxygen.txt`.

A1 and B1 were then tested consecutively using their unchanged values. Both
17-character values echoed completely and exactly once before Enter, proving
that the first Enter did not disable echo for the next numeric field. Reopened
M and read back both unchanged values. G/N returned to the main menu; H produced
`- passive -` and the Mag-Key wake prompt. COM11 is closed and free.
All planned echo checks and cleanup are complete.

Observed follow-up issues outside this echo fix:

- Esc at OX input rejects the value and returns to OX; it does not cancel the
  entire calibration dialog.
- The existing menu rewriter turns `Illegal value` into misleading
  `OSU: presenting instrument menu...` text even inside numeric entry.
- Reopening CDC after a long numeric-input wait can report a passive greeting
  even though the external instrument is still waiting for a number.

### Windows flashing note

Shell Eject of E: removed COM11 as well, so the first flash preflight refused
before programming. After operator USB reconnection and a repeated stop/flush,
a later check found no accessible OSU volume and COM11 still present; app-only
flash then passed its normal safety checks. The attempted `mountvol E: /P`
reported access denied; do not assume that command completed successfully.

## Self-test T extension

The operator also requested immediate `1-2-3-4` progress and final
`Functional test ok`, and asked for measured timing instead of relying on an
estimated minute per step. T selected from the main menu now activates the same
`shouldPassThroughUnterminatedRx` framing path used by numeric entry. Its own
bounded communication hold allows up to ten minutes instead of the ordinary
90-second menu hold. Y restarts the ten-minute deadline. Success detection works
whether progress shares the result line or arrives separately. G/H/R, normal
menu return, and measurement/passive boundaries release the self-test state.

Host regression passed for simulated minute-long pauses between stages, split
completion text at every byte, no duplicate progress, timeout, uptime wrap, and
return to normal line buffering. PCB 3.1.2 build passed.

Hardware verified on SN107 / COM11 after app-only flash through J-Link 69650428.
Programming verification and system reset passed. `V` confirmed build
`Sep 07 2026 14:26:39`, software 0.9.9P, PCB 3.1.2, working tree based on
`main@602becb1`.

Measured time from sending Y (host receive timestamps, approximately 0.2 s
resolution):

| Output | Since Y | Since previous stage |
| --- | ---: | ---: |
| 1 | 0.578 s | 0.578 s |
| 2 | 52.516 s | 51.938 s |
| 3 | 105.406 s | 52.890 s |
| 4 | 159.828 s | 54.422 s |
| Functional test ok | 222.719 s | 62.891 s |

The exact received test body was:

```text
Self-test
1-2-3-4
Functional test ok
```

Each stage arrived before the final CR/LF, exactly once. Communication remained
active beyond 90 seconds. Total duration was 3 minutes 42.7 seconds; retain the
ten-minute bound to allow instrument/test variation. Main-menu end marker and
subsequent `- passive -`/wake prompt were confirmed. COM11 was closed and is free.

Workspace evidence: `tmp/self_test_timing_20260907.log` (timestamped raw chunks),
`tmp/self_test_timing_20260907.json` (durations, transcript, final build identity).
The ad-hoc timing script sent G while the automatically returned menu was still
printing, so the cleanup menu excerpt is partial; the final menu marker and
passive exit were confirmed. This does not affect the measured self-test body.
