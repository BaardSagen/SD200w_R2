# Handover: automatic SD204/8 air-pressure setting after Mag-Key start

Date: 2026-09-02

Development branch: `airPress`

Integrated branch: `main`

Base history:

- `f84ffc1 fix(osu): forward start I to instrument`
- `4e515c8 fix(osu): serialize hidden-menu disk ownership`

## Behavior

`system.ini` now contains this default under `[instrument0]`:

```ini
enableAirPressureMeasurement=on
```

Older valid files that do not contain the key are interpreted as `on` and
migrated to the canonical file. `off` keeps the previous transparent
Instrument start behavior.

With the option enabled, a P0.25 Instrument ON/OFF assertion that was not
caused by a recently forwarded user start-I is treated as a customer Mag-Key
start. OSU first applies the existing immediate sensor-power policy, then
drives the SD204/8 protocol in this order:

1. `I` immediately stops the just-started measurement.
2. The complete A/S/H status menu is required before OSU sends `A`.
3. `Auto-setting <A>` is required before OSU sends the second `A`.
4. `Have instrument in air and press <R>` is required before OSU sends `R`.
5. OSU waits for `Initiated` and the complete returned A/S/H menu.
6. OSU sends `S`, waits through the status text for the complete
   `Press <M> for menu or wait 10sec` start prompt, then sends `I`.
7. A running/header/data line confirms the automatic sequence completed.

Measurement storage is blocked from the external Mag-Key assertion through
the complete pressure-setting transaction. The initial Instrument header and
any transient N-lines are displayed but are not counted, enriched, or written.
Storage opens on the first confirmed running/header/data line after the final
restart `I`, so the restarted Instrument header is the first header in the
customer's file. It then continues normally until Mag-Key stop/passive. An
aborted or timed-out transaction remains storage-blocked until passive, rather
than creating a partial session file.

The prompt parser accepts both supported A/S/H countdown endings:

- `If no command, instrument will go passive in 10 sec.`
- `If no command, measurement will start in 10 sec.`

Every protocol stage has a bounded timeout. SYSTEMOFF and MAX3222 shutdown are
held while the sequence is active. Critical-battery stop has priority. The
automatic attempt is latched once per real Instrument session and is re-armed
by a confirmed `- passive -` line, so periodic Cable Detect pulses cannot
restart the pressure sequence.

After one possible first-menu stall was observed without USB (followed by ten
successful no-USB repetitions), the quiet interval after every confirmed menu
boundary was increased from 160 ms to 250 ms. The initial stop-I remains
immediate. This removes USB CDC presentation time from the timing assumption
while remaining well inside each 10-second Instrument menu timeout.
The 250 ms value is an intentional field-risk tradeoff: a missed command leaves
the Instrument in a bounded menu that subsequently sleeps, and the customer
can retry the Mag-Key start. Increase the delay only if repeatable failures or
customer reports justify the added transaction time.

## Physical validation

Hardware:

- OSU107 SN107, PCB 3.1.2
- OSU CDC COM11, USB serial `OSU107-SN0107`
- J-Link COM6, probe serial `69650428`

The signed PCB 3.1.2 image was programmed with sector erase, verified and
reset. COM11 returned, and `E:\config\system.ini` was automatically migrated
with `enableAirPressureMeasurement=on` while preserving Instrument mode.

Two operator Mag-Key starts completed the response-driven sequence. The first
captured pressure changed from 953.36521 to 952.79857 mbar. The final automated
run verified ordered A -> A -> R -> S -> I output and received two N-lines.
The persistent P0.25 power window recorded three assertion edges across that
run, with maximum observed enable delay of 0 ms for P0.4 and 1 ms for the
analog front end. Only one pressure sequence ran despite the repeated edges.

A later storage-gating run started with 954.65545 mbar and completed automatic
setting at 953.60640 mbar. After two restarted measurements and an explicit
disk refresh, exactly one changed Instrument file was present:
`instrument/2026/09/2026_09_02_16-58-18_C.txt`. It contained exactly one OSU
header, one Instrument header (`AP0953.606`), one FIELDS header, and the two
post-restart rows. The initial 954.65545 mbar header was absent. The same run
again measured 0 ms maximum P0.4 delay and 1 ms maximum analog-front-end delay
over three P0.25 assertion edges. The Instrument was subsequently confirmed
passive.

A separate keyboard-start regression then passed:

- a raw I at the Instrument start prompt started measurement without invoking
  automatic air pressure;
- two measurements arrived;
- I stopped the Instrument;
- F/Y removed and restored CDC as COM11;
- a new host G reached the Instrument after reconnect;
- H restored passive state.

## Build and host verification

- Host interval/prompt/state-policy executable: PASS.
- Final pristine PCB 3.1.2 release build: PASS, flash 627180 B,
  RAM 203168 B.
- Final pristine PCB 3.3.0 release build: PASS, flash 627284 B,
  RAM 203168 B; build-only.
- 68 targeted Binder tests covering sensor-power and hidden disk reconnect
  behavior reached 100% passing testcases. The local pytest process retained
  an existing background thread after reporting 100%, so the runner itself
  was interrupted after all selected testcases had completed.

## Main integration and final 0.9.9O artifacts

`airPress` was fast-forwarded into `main` from `63098c7` through source/docs
commit `b4ca367`. Both hardware profiles were then rebuilt with pristine
sysbuild and update packaging. The images embed software version `0.9.9O`, Git
branch `main`, and commit `b4ca3673`.

Both update BIN signatures passed MCUboot `imgtool verify`:

```text
PCB 3.1.2 image digest: fedb575dc4b49cf861cecf06142af45d1046a734fa8151505fe044a771f3f725
PCB 3.3.0 image digest: 22bfb04f57f91bf5868668b67616ff08764500791e1d1dad38a1478ada421651
```

Final packaged files:

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9O.hex
  size 1765096
  SHA256 C19F67B939FA4F1E3E6152B80460836243563A3FD9F69051D45FBBF80F8842C3

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9O.bin
  size 627516
  SHA256 A4FAFFE29297E896DD6417C44438A9FDFA6265FC6F8E8465AC156D9BA5A86D3D

tools/flashTool/hexfiles/program/
  osu107_signed_hw3.3.0_0.9.9O.hex
  size 1765395
  SHA256 D22C712EDE51B64B3C9055591FD44A76DF8F30AA712890DD957535A895A9950E

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.3.0_0.9.9O.bin
  size 627620
  SHA256 D2318AA245741CF239A0C65AA3BDBBE51234071607E2C49AA7BB66B494D6BA01
```

Every packaged file was hash-compared with its corresponding pristine build
output and is byte-identical. The final PCB 3.1.2 source was physically tested
before the clean `main` rebuild; the packaged image differs only in build
timestamp, Git branch provenance, and the resulting non-deterministic RSA-PSS
signature, and was not reflashed after packaging. PCB 3.3.0 remains build-only.

Physical logs are stored outside the repository in the user's local Temp
directory with prefixes:

- `instrument_auto_air_pressure_final_20260902`
- `air_pressure_keyboard_i_usb_regression_20260902`

The Instrument was left passive. The active disk configuration remains
`surface.enable=0`, `instrument0.enable=1`, and
`instrument0.enableAirPressureMeasurement=on`.

## Corrected 0.9.9P release artifacts

The automatic-air-pressure and hidden-menu fixes were originally packaged
locally with the `0.9.9O` identity. Because version O had already been issued,
the follow-on release identity was corrected to `0.9.9P`. The O artifacts are
retained as historical files; the P files below are the release artifacts to
use for these changes.

Commit `9bfcd25` changes only the firmware version identity and changelog
classification. The functional source is therefore identical to the version
physically validated above. Both hardware profiles were rebuilt with pristine
sysbuild from `main@9bfcd25f`. The images embed software version `0.9.9P`.

- PCB 3.1.2: PASS, flash 627180 B, RAM 203168 B.
- PCB 3.3.0: PASS, flash 627284 B, RAM 203168 B; build-only.

Both update BIN signatures passed MCUboot `imgtool verify`:

```text
PCB 3.1.2 image digest: a3d4382ded8d44586072eff196e3b6dab69171186ff9b9ae74a238834fff6602
PCB 3.3.0 image digest: ea7f6af496224c0abebf882539bb6cdcfd65289438b4d7b9469dc11cca8f758e
```

Final 0.9.9P files:

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9P.hex
  size 1765096
  SHA256 8AAC038C1CF1D435848BEDEA0522A49D8C567FA47E7ABDD85520C47ABC96449A

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9P.bin
  size 627516
  SHA256 EEA9745C213001DB07C5B648A5DEF5CE0E86A25074625AA0D1CA5AC223FEA2B5

tools/flashTool/hexfiles/program/
  osu107_signed_hw3.3.0_0.9.9P.hex
  size 1765395
  SHA256 AC77F26931D1C5BC229CE5387BFE37190FE62D2F9BF261327C88FB8B44479806

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.3.0_0.9.9P.bin
  size 627620
  SHA256 128B1DA11EE6963F7AAC2501284FE337736840B4BFB741CFABC80078253E9C1A
```

Every P artifact was SHA-256-compared with its pristine build source and is
byte-identical. The P image was not reflashed because the only executable
difference from the physically tested build is the corrected version string
and resulting build/signature metadata.
