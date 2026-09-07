# Handover: replacement 0.9.9P range, UART-header and Mag-Key timing release

Date: 2026-09-03

Branch: `main`

> CURRENT FINAL STATE - READ THIS FIRST
>
> Every status, artifact, acceptance-gate, interruption and resume statement
> below that precedes `FINAL ACCEPTANCE` is retained only as historical context.
> The authoritative release state, artifacts and completed physical results are
> recorded in the final section of this handover.

Firmware source commit: `d5d0adfb` (MagKey/UART and pressure-restart corrections on top of
the one-second timing release from `9ddded11`)

Status: signed customer firmware produced for intensive testing on completed
products. The repeated MagKey stop/start failure was isolated from the field
sequence but this replacement was not physically exercised by Codex, so the
test matrix below remains a release-acceptance gate.

## Superseding P identity

The operator explicitly requested that the public firmware version remain
`0.9.9P`. These four files replace the same-named one-second P artifacts from
source `main@9ddded11`. Version text alone cannot distinguish them; the current
replacement must report Git source `main@d5d0adfb` and match the SHA-256 values
below.

This is a normal customer image, not a demo or mock build:

- `kSwVer` is `0.9.9P`;
- `kSwTag` and `kSwNote` are empty;
- no build `FileSuffix` was supplied;
- `CONFIG_OSUM_FWUPDATE_MOCK` is disabled in both profiles.

If this exact image passes completed-product testing, it can remain installed;
there is no demo marker that requires a later replacement flash.

## Corrected behavior

### Instrument range assertion

The SD204/8 can assert P0.25 Cable Detect while an active sensor changes range.
That edge was incorrectly eligible for the automatic air-pressure sequence.
The decision now uses a logical Instrument-session latch captured before the
edge. Bootstrap seeds that latch before UART consumers start from boot ownership
and retained session-path/N-line evidence. A confirmed passive response remains
authoritative and cannot be overwritten later by stale boot state.

Consequently, active, retained, RTC-woken and long-interval sessions reject the
edge without sending stop `I` or entering I/A/A/R/S/I. A fresh external Mag-Key
start remains eligible exactly once, including an early-header start with USB
and a no-USB wake. A keyboard-forwarded `I`, stopped/menu state and H/passive
remain ineligible.

### Corrupt Instrument header

The observed `CTDOTOF PAR OxR Ser No .47 OF044.50` header was not a direct array
index overrun. An incomplete UART stream prefix could survive a deliberate RX
flush or a queue loss and later be joined to an unrelated measurement tail.

UART1 queue entries now contain explicit payload length, RX-flush generation
and monotonic sequence. Buffer copy/reset is serialized. The consumer clears
its line carry at every generation change or detected sequence gap and rejects
already-dequeued stale fragments. This prevents an old measurement suffix from
being accepted and persisted as serial-number/air-pressure header content.

### Mag-Key air-pressure command timing

At the operator's request, the quiet interval after each confirmed menu
boundary in the automatic Mag-Key air-pressure sequence is increased from the
original 250 ms to a final 1000 ms. The intermediate 500 ms package is
superseded. The delay applies to the five follow-up commands A/A/R/S/I. The
initial stop-`I` remains immediate, so the five quiet intervals total five
seconds, 3.75 seconds more than the original 250 ms sequence.

The stopped/status menu allows 10 seconds for the first `A`; sending it after
one second leaves approximately nine seconds of margin. Once that `A` selects
air-pressure control, the Instrument expands the remaining command window to
one minute. OSU still uses its own bounded 12/15-second response safety
timeouts. The separate range-change rejection path never starts this sequence
and does not use the delay.

### Repeated MagKey stop/start sessions

The one-attempt-per-session latch was previously re-armed only by an explicit
`- passive -` UART status. A normal MagKey stop can instead complete the A/S/H
stop menu or end with the idle `Use Mag-Key ...` / `Start by Mag-Key ...`
prompt. The air-pressure attempt latch and logical measurement-session latch
could therefore retain the wrong combination. A later genuine MagKey start was
rejected, while its first range-change Cable Detect edge could be mistaken for
the still-pending start and trigger air pressure at the range change.

A completed stopped menu and both supported idle MagKey prompts are now
authoritative session-end evidence, except while OSU's own automatic pressure
transaction is active. A timestamp on an explicitly keyboard-forwarded `H`
keeps that user command ineligible, while a physical MagKey assertion after a
completed stopped menu is eligible. Each real passive-to-MagKey-start session
can consequently run exactly one air-pressure sequence at startup, leaving no
pending attempt for the first range change.

### MagKey UART transition and 7E1 range text

The MAX3222 fifteen-second hold was previously armed only by an OSU-originated
command. A physical MagKey stop could therefore let the transceiver turn off
before the optional ten-second passive/wake response. Both P0.25 assertion and
deassertion now force the communication path on immediately and hold it across
that response window.

COM11 raw capture also proved that the apparent wrong-baud startup bytes
`D2 E1 A0 2D CC 4D 8D` decode, after removing the 7E1 parity bit, to the valid
SD208 range marker `Ra -LM`. Explicit `Ra-`/`Ra -` range lines are now parsed
even during the main-menu-to-run transition, producing clean range handling
instead of forwarding high-bit text to CDC.

### Air-pressure restart and menu recovery

The expected `Start by Mag-Key or press <I>` line after the post-`Initiated`
status request was incorrectly classified as an external session end while the
automatic transaction was still active. That reset the state machine before
the following `Press <M> ...` boundary, so the final start `I` was not sent and
the Instrument eventually entered its full menu.

Idle/start prompts and the A/S/H stop menu no longer end an active automatic
pressure transaction; an explicit `- passive -` remains an immediate abort.
After the final `I`, measurement/header traffic completes the transaction. If
the Instrument instead reports `Menu:`, OSU sends one bounded recovery `R` and
waits for measurement traffic. A repeated failure times out without a command
loop.

## Verification

- Strict host policy/UART regression executable: PASS with
  `-Wall -Wextra -Werror`.
- PCB 3.1.2 SN107 app-only flash/verify: PASS. `VER` reported
  `0.9.9P`, PCB 3.1.2 and `main@d5d0adfb`; NVS/calibration were retained.
- Two consecutive COM11 MagKey starts completed the full automatic pressure
  sequence and final restart. Both reached `Running via OSU107`, a clean header
  and sequential N-lines. A preceding capture reproduced the old missing-I
  path and the 7E1 `Ra -LM` high-bit bytes used to verify the corrections.
- Final pristine PCB 3.1.2 package build: PASS; application flash
  628916 / 958464 B (65.62%), RAM 204320 / 262144 B (77.94%).
- Final pristine PCB 3.3.0 package build: PASS; application flash
  629004 / 958464 B (65.63%), RAM 204320 / 262144 B (77.94%).
- Generated configurations select only their intended hardware profile.
- `CONFIG_OSUM_FWUPDATE_MOCK` is disabled in both configurations.
- Both signed BIN files contain `0.9.9P` and `d5d0adfb`; searches found no
  `demo` or `mock` marker.
- MCUboot `imgtool verify` passed for both packaged BIN files.
- Each packaged BIN is byte-identical to its final `zephyr.signed.bin` and
  `osu107_update.bin` source.
- Each packaged HEX is byte-identical to its final `zephyr.signed.hex`; decoded
  HEX application payload is byte-identical to its matching BIN.
- PCB 3.1.2 and 3.3.0 produced identical MCUboot HEX files, matching the shared
  FlashTool MCUboot file.
- Final source/build diff checks passed. Build logs contain the known upstream
  Zephyr `nrf_qspi_nor.c` unused-variable warning and Zephyr's generic warning
  that the default USB VID must be configured for a USB product. Neither build
  reports a compiler or linker error.

MCUboot validation output:

```text
PCB 3.1.2 image digest: c08b2477807114a70fed36b7cde54fc47f4a78ad7dc098d1ba1ace5dc614d8ae
PCB 3.3.0 image digest: 1a15c01e90d41a0ef8e43611de0aa1309b020c0511426834da82fb90006b4188
```

## Replacement artifacts

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9P.hex
  size 1769985
  SHA256 C153AE6E4A29B90347555AE2DD23F2D4D32A7DB3E74B923C06B7666FE431A0CB

  osu107_signed_hw3.3.0_0.9.9P.hex
  size 1770226
  SHA256 A3A67F43DB827D077D8CF36934ED92FEF801CD5ED85418BD454CCB8C27BF6C49

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9P.bin
  size 629252
  SHA256 92CCF8E20B64E0CFA40B4C72EA1996F666C30A99AB13B6CDF3FB8C6C2CAE20C9

  osu_m_update_hw3.3.0_0.9.9P.bin
  size 629340
  SHA256 02E155A6705C947F25F48E5642774072F2F7028CC220718E8EE87BAA4AE5851C

tools/flashTool/hexfiles/mcuboot/
  zephyr.hex
  size 104327
  SHA256 13B636711AF7C2897F20A5AD37440BFB1D08E2CB4EFD4A86F1DA3F58F36AF91E
```

The MCUboot header version remains the established signer default
`0.0.0+0`; the product-visible version is `0.9.9P`.

## Completed-product acceptance matrix

Before customer shipment, test the exact packaged PCB-matching image:

1. Confirm `VER` reports `0.9.9P`, `main@d5d0adfb`, the correct PCB revision,
   and no bracketed demo/tag suffix.
2. Run an extended active Instrument measurement while deliberately forcing
   multiple 7E1 `Ra-MV`/range changes. Require zero automatic stop-I messages,
   zero air-pressure menu transactions, uninterrupted counters and one session.
3. Repeat at least three consecutive real Mag-Key stop/start cycles without a
   PC/USB command between them, then repeat with USB connected. Every fresh
   start must run exactly one complete pressure sequence. After every start,
   deliberately force the first range change and require no additional
   air-pressure transaction. Require an immediate
   initial stop-`I`, the 1000 ms quiet interval after each confirmed
   menu boundary, first `A` within its 10-second menu and the later commands
   within the Instrument's one-minute window. Require exactly one complete
   I/A/A/R/S/I pressure sequence per passive-to-active session and no initial
   transient rows in storage.
4. Exercise keyboard `I`, full-menu `H`, stopped menus and immediate
   passive/restart transitions. None may be misclassified as a second automatic
   pressure run.
5. Exercise long Instrument intervals and RTC/SYSTEMOFF wakes with a retained
   path and retained-N-only state. Require zero pressure-setting commands and no
   duplicate header/CALSYS/session.
6. Stress repeated UART flush/menu/USB reconnect/power-cycle paths. Every stored
   Instrument mode header must contain the exact serial number and plausible AP;
   reject any measurement-tail text in those fields.
7. Audit all resulting files for fixed field counts, sequential counters,
   complete line endings and valid ASCII, then stop logging, perform the normal
   disk handoff and run a read-only filesystem check.
8. Repeat critical-battery interruption tests before shipment if automatic air
   pressure is enabled.

PCB 3.3.0 remains build/package-only until an assembled 3.3.0 card completes
the hardware approval matrix. Never install a 3.1.2 image on 3.3.0 or vice
versa.

## Flash safety

No product was flashed while producing this package. Follow the current
`osu107/README.md` stop, drain, `USBD U`, Windows-eject and exact-probe procedure.
Use application-only flashing when NVS/calibration must be retained. Selecting
MCUboot/full flash erases internal NVS. For firmware update, copy the BIN that
matches the physical PCB and rename the destination exactly
`update/osu_m_update.bin`.

## SN105 repeated-start correction (supersedes the replacement artifacts above)

The earlier `main@d5d0adfb` P image was reproduced failing on SN105 (PCB 3.1.2,
COM15). After a clean passive message, a later Mag-Key start could go directly
to Date/CTDOF/N rows without performing the required air-pressure sequence.
`config/system.ini` still contained `enableAirPressureMeasurement=on`.

Direct PWRWIN capture proved that the failing start had exactly one valid Cable
Detect edge: the input changed HIGH/passive to LOW/active, P0.04 enabled at
0 ms and AFE enabled at 1 ms. This excludes Mag-Key hardware, edge timing, UART
shutdown and the air-pressure delay as the cause. The software retained a stale
logical-session latch after the newer confirmed UART passive boundary.

Source commit `e9bef870` makes the confirmed passive/stopped boundary
authoritative when classifying the next Mag-Key assertion. It also postpones
consuming the one-shot automatic-pressure attempt until after active-session,
configuration and in-progress guards have accepted the start. A rejected range
edge therefore cannot consume the next genuine Mag-Key attempt.

Verification completed:

- Host interval/policy test passed, including every combination of logical
  session state and confirmed passive boundary.
- Pristine PCB 3.1.2 and PCB 3.3.0 Zephyr/MCUboot builds passed.
- The build configurations select the matching PCB and have
  `CONFIG_OSUM_FWUPDATE_MOCK` disabled.
- MCUboot signature verification passed for both update BIN files.
- Every packaged artifact is byte-identical to its pristine build output.

The same P filenames are retained. These files replace the earlier artifacts:

- `osu107_signed_hw3.1.2_0.9.9P.hex`: 1,769,981 bytes, embedded build
  `Sep 03 2026 16:55:17`, SHA-256
  `B9701F5E76055835EB030340FCEE398D98B383D1BC352370271EEDF07D23B7BE`.
- `osu_m_update_hw3.1.2_0.9.9P.bin`: 629,252 bytes, SHA-256
  `5F7583B246FC7210BD4224CD8DBAB857D5FBC633CA9A3C074A93FA82E32A43`;
  verified image digest
  `96b9ae4f4a6995f7df04f376ac0a682b2a548405339015c3a46096e76a9632ef`.
- `osu107_signed_hw3.3.0_0.9.9P.hex`: 1,770,267 bytes, embedded build
  `Sep 03 2026 16:57:39`, SHA-256
  `FD59E03B190C9DCF1B44A3E046069FD412DCC108038554BC7D6F6CE928E1B21C`.
- `osu_m_update_hw3.3.0_0.9.9P.bin`: 629,356 bytes, SHA-256
  `93E1E5ED40D38C665B7C71F8EE25829C983728E1DF45785E7B2C89A65B0B4651`;
  verified image digest
  `7dc6f3c0e097c21165d20e3894cc728e9450179ae93d463518492d31d24184e8`.

The connected SN105 was observed using the older 15:44 image and was not
automatically flashed. The new 3.1.2 image still requires physical acceptance
on SN105: at least three consecutive Mag-Key stop/start cycles without an
intervening PC session, with exactly one air-pressure sequence on every start
and none on the first subsequent range change.

## Reboot handover: silent Mag-Key stop fallback and interrupted COM11 flash

### New physical finding

SN105 was updated to `main@e9bef870` (build `Sep 03 2026 16:55:17`), but the
second-start failure was reproduced again. A controlled COM15 run started from
a stable passive P0.25 HIGH state. Mag-Key produced exactly one valid assertion
edge; P0.4 and AFE were both ready within 1 ms. Nevertheless the Instrument
went directly to its Date/header and N rows without the automatic stop-I or
air-pressure transaction.

This proves that `e9bef870` still depended on a UART passive/menu line to re-arm
the one-attempt-per-session latch. The failing SD204/8 unit does not always
send that line after a physical Mag-Key stop. The Instrument variant exposes
the omission, but OSU firmware must tolerate it.

### Source correction ready

Commit `33214d0` (`fix(osu): rearm MagKey after silent passive stop`) adds a
physical fallback. P0.25 must remain continuously deasserted for 4500 ms, the
same duration as the existing range-pulse session hold, before OSU treats the
state as a real session end without UART evidence. This re-arms automatic air
pressure and clears the logical session through the normal passive callback.
Short range-change pulses remain ineligible. The fallback is disabled while
the I/A/A/R/S/I transaction owns the stopped interval.

The host interval/policy test passed, including short range pulse, sustained
deassert, automatic-transaction exclusion, one-shot behavior and uint32 uptime
wrap. A pristine PCB 3.1.2 sysbuild completed successfully:

- firmware source: `main@33214d0`;
- embedded build time: `Sep 03 2026 17:49:14`;
- application flash: 629,408 bytes; RAM: 204,320 bytes;
- `CONFIG_OSUM_HW_REV_3_1_2=y`;
- `CONFIG_OSUM_FWUPDATE_MOCK` disabled;
- signed build files are under
  `osu107/build-3.1.2/osu107/zephyr/`.

PCB 3.3.0 and the four same-named distribution P artifacts have **not** yet
been rebuilt/replaced for `33214d0`. Do that only after the physical COM11 test
passes, then commit the replacement artifacts and update their hashes here.

### Flash interruption and exact recovery state

The problematic SD204/8 was moved to OSU SN107, with OSU CDC COM11 and J-Link
VCOM COM6. Probe serial `69650428` is the only ID reported by `nrfjprog --ids`.
Surface was already stopped, Instrument was passive, and USB Disk `U` returned
`OK` before each attempt.

Windows File Explorer eject removes the entire OSU USB composite on this PC,
including COM11. A selective exclusive volume lock/dismount was therefore used
and the guarded app-only flash preflight passed with COM11 alive and MSC
inaccessible. `nrfjprog --program ... --sectoranduicrerase --verify` then ran
unusually slowly without completing. The operator had disconnected USB during
the first attempt; a second undisturbed attempt also remained active for
several minutes. It was explicitly terminated before the requested PC reboot.

No `nrfjprog`, J-Link or temporary volume-lock process remained at handover.
The volume lock was released. The second app-only attempt may have left the
primary application slot incomplete. MCUboot was not erased or programmed,
and the operation did not request a full chip erase, but the unit must not be
used until application programming and verification complete successfully.

### Resume after PC reboot

1. Confirm source commit `33214d0` and preserve unrelated dirty calibration,
   binder and mvProvision files.
2. Connect only the intended SN107/COM11 unit and J-Link `69650428`; leave the
   Instrument passive. Confirm `nrfjprog --ids` and inspect whether COM11 boots.
3. Investigate the slow `nrfjprog` path before another write. Check for stale
   Nordic/J-Link processes and test a read-only probe operation. Do not assume
   the interrupted primary slot is bootable.
4. Stop Instrument/Surface, flush USB Disk with `U`, and ensure Windows cannot
   access its volume while CDC/VBUS remains connected. Do not use the unsafe
   mounted-volume bypass on this installed unit.
5. Run guarded PCB 3.1.2 app-only flashing with probe `69650428`, allow
   program/verify to finish, perform the single checked reset, and require COM11
   `VER` to report `0.9.9P`, PCB 3.1.2, build `Sep 03 2026 17:49:14`, and
   `main@33214d0`.
6. With the problem SD204/8 still attached, test at least three consecutive
   Mag-Key stop/start cycles. Wait at least five seconds in the passive/high
   state between cycles. Require exactly one air-pressure sequence at every
   start and no sequence on any first range change.
7. Only after that pass, rebuild PCB 3.3.0, replace all four same-named P HEX/BIN
   distribution files, verify signatures and hashes, and update this handover.

## FINAL ACCEPTANCE - authoritative current state

This section supersedes every earlier status, artifact, acceptance-gate,
interruption and resume instruction in this handover. Those sections are kept
only to preserve the investigation chronology.

The root cause was session-boundary timing, not FAT or USB disk ownership. An
`F` disk refresh merely added enough delay and activity to mask the race. The
first robust correction was source commit `8999057` (`fix(osu): decouple
MagKey rearm from disk timing`), followed by final source commit `602becb1`
(`fix(osu): harden MagKey rearm ordering`). The established public firmware
identity remains `0.9.9P`, using the standard hardware/version artifact names.

For a silent stop in continuous-header modes, the physical fallback requires
P0.25 to remain continuously deasserted for 4500 ms before the end of a session
is qualified. An explicit UART passive/stopped boundary can qualify it earlier.
When relying on the physical fallback, waiting approximately 5-10 seconds after
a Mag-Key stop is the practical rule before starting again. A restart before
either boundary has qualified the stop is intentionally treated as the same
session, so it does not repeat an air-pressure transaction whose value cannot
have changed meaningfully in that short time. No `F` refresh or Ctrl+T service
menu is required.

### Final PCB 3.1.2 artifacts and physical acceptance

A pristine PCB 3.1.2 build completed successfully. The standard distribution
pair was committed in `e59f459` (`release(osu): package tested hw3.1.2
0.9.9P`):

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9P.hex
  size 1774440
  SHA256 FE836CCBAFC0F9F62BD7C5F228F718054BC11F095335EEF72A8D73B7D0D81C46

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9P.bin
  size 630836
  SHA256 1A873F645E7E45252B0C03B577C5F93EF8B7715450C1F6FC29ABB481BF093917
```

Both packaged files are byte-identical to the signed outputs used for the
successful SN107 flash. MCUboot `imgtool verify` validated the signed update
BIN with image digest
`08e82433b330e8a998ce4784fac9882e56ea70dfd0caadac768702605fa09b42`.

The PCB 3.1.2 application was flashed directly to SN107 using J-Link probe
`69650428`. The guarded app-only erase/program/verify operation and the final
reset all completed successfully. MCUboot was not replaced. Internal NVS and
its calibration data were preserved, and the external FAT filesystem was also
preserved.

Physical acceptance results:

- With OSU USB connected, three automatic air-pressure starts completed. The
  latter two followed real Mag-Key stop/start cycles with no intervening `F`.
  The stored AP values were `1006.17549`, `1007.06848` and `1005.72606`.
- With OSU USB disconnected, both the first and second consecutive Mag-Key
  starts performed automatic air pressure without `F`.
- After reconnecting OSU USB, `E:` remounted normally and `CHKDSK` reported a
  clean filesystem.
- The operator also reported a successful PCB 3.1.2 test on OSU SN105 / COM15
  using the same standard 3.1.2 artifacts. The observed 5-10 second wait
  between stop and the next start matched the intentional session policy.
- No Ctrl+T service menu was used or required during flashing or acceptance
  testing.

The original disk-ownership symptom is therefore closed on the tested PCB
3.1.2 units SN107 and SN105. Automatic air pressure re-arms across qualified
physical Mag-Key sessions with or without PC/USB disk ownership and without an
`F` refresh.

### Final PCB 3.3.0 build-only artifacts

The PCB 3.3.0 profile was pristine-built and packaged with build stamp
`Sep 03 2026 21:16:59` and embedded provenance `main@e59f459e`. Its signed BIN
passed MCUboot `imgtool verify`, and both packaged files are byte-identical to
their corresponding pristine build outputs.

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.3.0_0.9.9P.hex
  size 1774685
  SHA256 A2D2FD7CFBD38D77BBE7EA0734EDB651AA263BC691D7CA2DDCB73F33739C043E

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.3.0_0.9.9P.bin
  size 630928
  SHA256 6879E0E6EFBDAE4E988E1148C7292F83049EF757B43533FD6531784FFCCC45F9
```

The verified PCB 3.3.0 image digest is
`52a0fe3e785560ef9aa9c4f398f86ec01fa6239c2e83f158548bc876125a3cb1`.
PCB 3.3.0 remains build/package-only and has not been tested on assembled
3.3.0 hardware. Its existing unvalidated-hardware flashing guard remains in
force.
