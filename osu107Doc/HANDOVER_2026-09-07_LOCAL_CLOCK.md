# Local clock setting in OSU107 and Surface

## User agreement

- X is the shared local clock command. W belongs to a hidden instrument menu.
- Show a format and example, echo every entered character, then ask Y/N whether
  to change the current LT label to GMT or vice versa after setting the clock.
- OSU107 uses G to return to the combined instrument/OSU107 menu. Surface uses Esc.

## Behavior and implementation

- `services_wiring_bootstrap.cpp` owns one local clock dialog for both modes.
  The menu shows `Set OSU date & time <X>` or `<X> Set logger date & time`.
  Passive OSU107 also accepts X locally, using the hidden-U routing policy;
  instrument submenus retain their input and active logging is rejected.
- Input format is `YY-MM-DD-HH-MM-SS`, years 2000-2099. Example:
  `26-09-07-15-30-00`. `local_clock_input.hpp` validates actual calendar dates
  and time bounds and handles character echo, pasted input, CR/LF and correction
  with Backspace/Delete. Invalid input does not write the clock.
- Enter sets the external RV3028 and synchronizes the internal nRF clock.
  The subsequent Y/N question changes only the persisted LT/GMT label, without
  applying a timezone offset. N retains the current label.
- G/g in OSU107 or Esc in Surface cancels before Enter without changing time.
  After Enter, it keeps the newly set time and current label. The OSU107
  navigation hint on exit now depends on total time since X was opened: over
  60 seconds shows `Hold I to wake instrument`, otherwise `<G> for Menu`.
  No automatic G is sent on exit. Surface returns to its own menu.
- The dialog expires after 120 seconds without input. Timeout after Enter keeps
  the set time and existing label. Unsolicited instrument output is suppressed
  while entering local values. CTD S and the existing Q synchronization remain.

## Verification on SN107, PCB 3.1.2, COM11

- Host C++17 test `local_clock_input_test.cpp`: valid/leap dates, invalid dates
  and time bounds, split input/CRLF, per-character echo, correction and overflow.
- Device: invalid 2026-02-29 rejected; valid 2024-02-29 accepted; all 17 typed
  characters echoed once; Backspace echoed one erase sequence; pasted CRLF works.
- LT -> GMT -> LT persisted and read back without shifting entered hours.
- Surface X works; X during logging asks to stop; test logging was stopped.
- Final build `Sep 07 2026 16:03:11`, version 0.9.9P, app-only flashed and verified
  with J-Link 69650428. OSU107 X advertises G. G during partial input and g+CRLF
  after Enter both returned the full CTD menu with OSU107 options, including X.
- Internal/external RTC comparison after setting: delta=0s.
- Final firmware Surface test: Esc cancelled partial entry and returned the
  Surface menu. Original system.ini restored byte for byte and applied back to
  OSU107. Left stopped/passive with PC local time (LT); COM11 closed.
- Serial evidence: `tmp/local_clock_after.log`. Test config backup:
  `tmp/local_clock_system_original.ini`.

## Follow-up UI revision

- Removed `(years 2000-2099)` from the format line; validation is unchanged.
- Prompt is `Current timezone is (LT) change to GMT? (Y/N)` or the reverse.
  Removed the explanation beginning `Y changes the label`.
- Added a separate monotonic entry timestamp. Typing refreshes the 120-second
  inactivity deadline but never restarts the elapsed-time measurement.
- OSU107 exit displays `<G> for Menu` up to and including 60 seconds, and
  `Hold I to wake instrument` after 60 seconds. Normal inactivity timeout also
  displays the wake hint; communication takeover/logging interruption does not.

Follow-up device verification: app-only flash verified on SN107, build
`Sep 07 2026 16:31:33`. Entry/Enter/N completed in 1.719 seconds and displayed
`<G> for Menu`; G then returned the combined menu. A second dialog accepted
partial input at entry and again after about 34 seconds; G at 65.016 seconds
displayed `Hold I to wake instrument`. Reopening CDC confirmed the instrument
was passive. New LT question and removed explanatory text verified on device.
No configuration changes; existing clock time base retained. COM11 closed.

Surface confirmation prompt ends with `<ESC> Menu:`. N already retains the
current LT/GMT choice; Esc is presented as menu navigation. The clock has
already been set by Enter.

Final Surface wording flashed and verified on SN107, build Sep 07 2026 16:53:23.
Observed `<ESC> Menu:` after Enter and confirmed Esc returns to Surface menu.
Device left in its existing Surface mode, stopped, LT retained; COM11 closed.

## Release artifacts: 0.9.9Q

The release version is **0.9.9Q**, corrected from the initial P packaging in
commit d300167. Both firmware builds now embed 0.9.9Q; this is not a filename-only
change. Original P artifacts were restored from d300167's parent to preserve
the previous release. Q includes numeric C/M echo, T self-test streaming,
hidden passive U, and local X clock setup with the final `<ESC> Menu:` prompt.

Build stamps:
- PCB 3.1.2: `Sep 07 2026 17:06:46`.
- PCB 3.3.0: `Sep 07 2026 17:07:12`.

Both builds and MCUboot signatures passed. HEX images decode to the matching
signed BIN at 0xC000; embedded version strings were checked. The implementation
was hardware-tested on SN107/PCB 3.1.2 before the version-only rebuild. Q with the mode-exclusion fix was subsequently flashed and tested on SN107;
PCB 3.3.0 remains build-tested only.
MCUboot is unchanged, including existing image-version metadata 0.0.0+0.

Host tests passed before version bump: instrument_rx_stream_test (including
self-test policy), instrument_update_config_policy_test, local_clock_input_test.
See the separate numeric-echo and hidden-update handovers for those changes.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/flashTool/hexfiles/updateBin/osu_m_update_hw3.1.2_0.9.9Q.bin` | 635580 | `3e6840e8a3ea84564b635fbcf20e6b6ece48b86551226d14bf2f259bfb30b47c` |
| `tools/flashTool/hexfiles/program/osu107_signed_hw3.1.2_0.9.9Q.hex` | 1787776 | `9536e5575daf100fd2352da39b73e993cafc6fedf13f92479b3d7b8afa71009d` |
| `tools/flashTool/hexfiles/updateBin/osu_m_update_hw3.3.0_0.9.9Q.bin` | 635672 | `29a3e3205a3309f2d73a274bd64e2eef99cd80a136b6f9ea3da3a2d9bf65fd13` |
| `tools/flashTool/hexfiles/program/osu107_signed_hw3.3.0_0.9.9Q.hex` | 1788038 | `997836408879579137d9f5e05b7770fdf58d84eaf586b10718c60f778a93054d` |

## Mutually exclusive logger modes

`loadAndValidateAllFromDisk` now rejects surface.enabled && instrument0.enabled
before publishing staged data or committing NVS/runtime policy. MIR and APPLY,
including the U shortcut, use this shared validation. The message identifies
both modes and asks to set [surface] enable=0 or [instrument0] enable=0.
Existing NVS parsing/migration is unchanged; this does not reset old persisted
configurations merely because they had both permission gates enabled.

Hardware test on SN107/Q: MIR and APPLY rejected 1/1, with staged-unchanged and
APPLY-aborted messages. MIR and APPLY accepted 0/0, 0/1 and 1/0. Original Surface
system.ini was restored byte-for-byte and APPLY reported no changes vs NVS.
Evidence: tmp/mode_exclusion.log; original: tmp/mode_exclusion_original.ini.
The cleanup V key briefly invoked read-only calibration verification in Surface
rather than hidden version display; it did not change configuration.

## Final Q package refresh

Regenerated signed BIN/HEX pairs for both PCB revisions from the final Q build
outputs containing the MIR/APPLY mode-exclusion fix (source commit 660dabc).
No source changes since the hardware-tested build; build timestamps above
remain valid. RSA-PSS re-signing changes artifact hashes, now updated in the
table. Signatures, embedded Q version, mode-exclusion message, and HEX/BIN
byte equality were checked again. No additional device flash was performed.

NRFADC clarification: current system-voltage measurement uses internal 0.6 V
reference, gain 1, and the configured 10 Mohm / 300 kohm divider, giving nominal
full scale of 20.6 V at the divider input. This is a measurement-range calculation,
not the board's verified maximum supply rating. No ADC settings were changed.
