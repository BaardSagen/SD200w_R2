# Handover: OSU107 0.9.9O USB MSC/CDC recovery and fixed-schema nan placeholders

Date: 2026-09-01

Branch: `main`

Target: `0.9.9O` post-candidate fixes

Source commit: `6170fd2 Fix CDC receive after USB refresh`

Artifact commit: the commit containing this finalized handover and the four
replacement O artifacts.

This document is a delta to
`HANDOVER_2026-08-30_COMPACT_IMMEDIATE_STORAGE.md`. The earlier handover
describes the base O compact-storage candidate. This handover records the USB
disk-handoff recovery, terminal workflow, fixed measurement schema, physical
tests, and replacement O artifacts produced after that candidate.

Hardware used for physical validation:

- OSU107 SN107, PCB 3.1.2
- OSU107 USB CDC COM11
- J-Link CDC COM6
- J-Link probe serial 69650428
- OSU FAT volume E:

PCB 3.3.0 remains build-only and has not been physically validated.

## Status

The USB recovery and user workflow are physically verified on SN107 in both
Surface and Instrument mode. A later Instrument `R` -> `I` -> `F`/`Y` test also
exposed and fixed a separate one-way CDC receive failure after software USB
refresh. The fixed-schema `nan` handling passes host tests, PCB 3.1.2 and 3.3.0
firmware builds, signed-image verification, and independent read-only code
review. A real ADC/IMU failure has not been deliberately injected on hardware,
so physical observation of a newly emitted `nan` remains a follow-up test.

The firmware version remains `0.9.9O`. The hardware-labelled O HEX/BIN files
from the earlier candidate must be replaced by the files recorded in this
handover; the filename alone does not distinguish the earlier candidate from
this post-candidate build.

## Original USB failure

The failure was reproducible when logging started without USB and USB was
inserted while logging was active:

1. The firmware owned and wrote the FAT volume.
2. Windows attempted to enumerate the unavailable mass-storage medium and
   could show a format prompt.
3. The user stopped logging from CDC or MAG and requested disk refresh with
   `F`.
4. In the failing state the disk remained unavailable. In some attempts both
   COM11 and the disk disappeared and did not recover after an OSU USB
   disconnect/reconnect.
5. A PCB reset or `CTRL+T`, `SLP`, `RESET` recovered the composite USB device;
   stored files remained intact.

An early implementation stopped and restarted the complete composite USB
device to hide MSC while leaving the logger active. CDC and MSC are part of
the same legacy composite device and cannot be independently removed by that
mechanism. More importantly, Zephyr 3.7's legacy Nordic USB driver could
complete only half of a re-attach when VBUS was already present: USBD was
enabled, but endpoints and the D+ pull-up remained disabled because the
edge-driven USB power-ready event had already occurred. That state explained
the simultaneous loss of COM11 and MSC.

## Final USB ownership behavior

The composite USB device remains alive while logging. CDC therefore remains
available for terminal data and commands. When firmware owns the FAT volume,
the legacy MSC implementation reports the removable medium as not present:

- `TEST UNIT READY` fails;
- `READ CAPACITY`, `READ`, `WRITE`, and `VERIFY` are rejected;
- `REQUEST SENSE` reports `NOT READY / MEDIUM NOT PRESENT`;
- host writes remain physically blocked by the wrapped disk-write barrier.

This makes Windows treat the interface like an empty card reader instead of
an unformatted writable disk. It avoids exposing FAT sectors concurrently to
Windows and firmware without tearing down CDC.

Disk ownership is now based on actual storage activity, not merely on the
instrument being awake or a logger mode being selected:

- Instrument claims storage when a measurement is queued for writing.
- Surface claims storage immediately before writing its session header and
  retains ownership while session writes are pending.
- Opening a startup/status menu before the first stored measurement does not
  itself lock the disk.
- Stale recent-N-line state is ignored after a confirmed Instrument passive
  transition.
- A completed `F`/`Y` handoff releases storage only after queued writes drain
  and the disk is flushed.
- Starting another measurement revokes an earlier host handoff.

Once Windows has observed the protected medium, MSC remains latched closed
until an explicit refresh or a real physical USB disconnect. This prevents a
short idle gap from reopening the FAT volume between logger operations.

`F` is accepted directly from the safely stopped Instrument state; the user no
longer needs to send `S`, then `M`, before requesting a refresh. The old
15-second refresh inhibit is no longer a precondition for disk ownership. A
15-second SYSTEMOFF inhibit is armed only after an actual refresh transaction
has been accepted, so the MCU remains awake while USB re-enumerates.

If storage becomes busy during the refresh race, the firmware re-enables USB
in protected mode and returns `-EBUSY` instead of leaving the composite device
disabled. User-facing refresh commands report the busy/error result.

## Nordic legacy USB recovery override

`cmake/osum_nrfx_usb_override.cmake` generates a checked local copy of
Zephyr 3.7's `usb_dc_nrfx.c` and replaces exactly one upstream source in the
USB driver target.

During `USBD_ATTACHED`, it checks the current Nordic USB regulator state. If
VBUS is already ready and USBD has not started, it queues the missing
`USBD_POWERED` transition. `USBD_POWERED` is idempotent and also handles a
late duplicate power-ready interrupt. This guarantees endpoint setup and D+
pull-up activation after an in-place refresh.

This is a targeted compatibility fix; upgrading Zephyr is not required for
the validated O behavior. The CMake override deliberately fails configuration
if its upstream anchors or source count change, so a future Zephyr upgrade
must review the override rather than silently applying it to different code.

## Follow-up: one-way CDC after Instrument refresh

Two different conditions initially looked like the same failed `G` command:

1. The CTD's short stopped menu accepts `A`, `S`, and `H`; `G` is not valid
   there. Before an Instrument `F`/`Y` refresh, OSU now sends `S`, waits for the
   returned `Press <M>...` prompt, sends `M`, and waits for the final full-menu
   line. The refresh is cancelled if either response is missing or the state
   changes.
2. A real one-way CDC state also existed. OSU could still transmit text to the
   PC through the CDC IN endpoint, while every PC-to-OSU command was NAKed on
   the CDC OUT endpoint. Zephyr 3.7 legacy `usb_disable()` detached the
   controller and cancelled transfers without publishing `DISCONNECTED` or
   `RESET` to the CDC class. Its internal `configured` flag therefore stayed
   true and the next `CONFIGURED` event did not queue a fresh OUT read.

The final lifecycle sequence is specific to the validated nRF52840 legacy USB
stack:

- validate the CDC class and callback before changing USB state;
- detach the nrfx controller and flush queued controller events;
- invoke the CDC class's own `USB_DC_DISCONNECTED` callback so `configured`
  becomes false;
- call normal `usb_disable()` to cancel transfers and disable endpoints;
- on re-enable, let `CONFIGURED` arm a new CDC OUT read and then restore the
  application UART callback/RX IRQ.

The second nrfx detach performed inside `usb_disable()` is idempotent. If CDC
cannot be prepared safely, refresh fails closed before normal USB disable and
marks MSC for rebind instead of claiming success with an uncertain receive
path. A compile-time guard prevents this legacy-only class cast from silently
being reused with `CONFIG_USB_DEVICE_STACK_NEXT`.

An upgrade is not required for O. Current legacy-stack code retains the same
lifecycle gap; a future migration to `device_next` is a separate project
because the product's dynamic A/B MSC binding, write guard, flash-disk override,
and Nordic attach compatibility code must be ported together.

The 15-second value discussed during diagnosis is not a delay before disk
access is granted. It is only a bounded SYSTEMOFF inhibit started after an
accepted refresh so the MCU remains awake while Windows re-enumerates USB.

## User-visible stopped and refresh workflow

The shared hint is:

```text
To see latest data on disk, refresh disk with <F>.
```

It is shown after:

- Instrument is stopped and reaches the prompt that otherwise goes passive
  after 10 seconds;
- Instrument is stopped by MAG and presents passive/stopped status;
- Surface is stopped with keyboard `I`;
- Surface is stopped with MAG while CDC is connected;
- a stopped CDC greeting when a disk refresh is still required.

The Instrument startup prompt saying it will *start* in 10 seconds is kept
separate and does not receive the stopped-data hint.

Surface MAG stop now returns the completed stop state to the main loop. With
USB present, the firmware emits a fresh stopped status/greeting after the
logger has drained and stopped, including the refresh hint. LED behavior is
unchanged.

Changing the Surface interval while stopped updates NVS and `system.ini`. If
the disk file was changed and USB is connected, firmware drains/flushed local
writes, then automatically refreshes USB after a 3-second notice. A failed
refresh reclaims storage and reports the failure. It no longer leaves USB
permanently absent after an interval change.

## Fixed measurement schema with `nan`

Before this fix, a mux-select error, ADC read error, or empty sample vector
silently omitted the affected token. In compact storage every following value
then shifted one column to the left. The concrete observed example was an
Instrument row with 11 values for a 12-field schema: `Par` was absent and the
valid `OxR=0.29` value occupied the `Par` position.

Every enabled and valid analog channel now emits exactly one token per row:

- a formatted measurement on success; or
- the literal `nan` on service, initialization, power, mux-enable, ADC-begin,
  mux-select, ADC-read, or empty-sample failure.

Full/live examples are `<prefix>nan<unit>`, such as `Parnan` or `CH2nanmV`.
The compact parser recognizes the configured prefix and unit and stores the
value as `nan` in the correct field.

Tilt follows the same invariant when Tilt belongs to the expected schema. A
failed read or formatter emits `<prefix>=nan<unit>`, for example
`Tilt=nandeg`; compact storage strips the prefix/unit and retains `nan` in the
Tilt column. DATE and TIME therefore stay in their declared positions.

Instrument takes one stable staged-configuration snapshot for the analog
channel list used through the complete sample. Surface continues to use its
immutable session configuration. Independent review found no path that emits
both a value and `nan`, or omits an expected token, for the handled failures.

Existing files are not rewritten. The pre-fix short row remains useful
diagnostic evidence.

## Physical USB validation

The user validated the following final flow on SN107:

1. Start Surface with MAG while OSU USB is disconnected.
2. Allow several measurements, then insert USB.
3. Confirm Surface data continues on COM11 while MSC remains protected.
4. Stop with MAG and receive stopped status plus the `F` refresh hint.
5. Use `F`/confirmation and confirm the current disk becomes available.
6. Repeat with keyboard stop; result passed.
7. Repeat the equivalent workflow in Instrument mode; result passed.

The prior COM11/MSC disappearance was also reproduced during development and
recovered with PCB reset before the Nordic attach fix. After the final fix,
application programming/verify/reset succeeded and both COM11 and the FAT
volume returned.

## Log and FAT integrity audit

The six newest test files were checked byte-by-byte and structurally:

| Mode | File time | Rows | Result |
| --- | --- | ---: | --- |
| Surface | 09-48-13 | 5 | Complete |
| Surface | 09-50-35 | 16 | Complete |
| Surface | 09-52-41 | 23 | Complete |
| Instrument | 09-58-27 | 5 | Complete |
| Instrument | 09-59-33 | 34 | Complete |
| Instrument | 10-03-02 | 4 | One pre-fix row missing `Par` |

All files contained valid ASCII, no NUL bytes, complete line endings,
sequential local counters, and monotonic timestamps. Session counters were
continuous:

- Surface: `2794 + 5 = 2799`, then `2799 + 16 = 2815`.
- Instrument: `8984 + 5 = 8989`, then `8989 + 34 = 9023`.

The short Instrument row was complete through its terminating CR, and later
rows were correct. It was a logical sensor dropout, not a torn append or FAT
corruption.

A final read-only `chkdsk E:` returned exit code 0:

```text
Windows has scanned the file system and found no problems.
No further action is required.
```

The checked FAT volume contained 8,351,744 bytes total, 1,073,152 bytes in 199
files, and 7,237,632 bytes free, with 2,048-byte allocation units.

`E:\FOUND.000\FILE0000.CHK` is an older 4,096-byte recovery file dated
2026-08-27. It was not created by the 2026-09-01 tests.

## Verification completed before source commit

- Host interval/policy/schema test compiled and returned exit code 0.
- Full PCB 3.1.2 sysbuild completed.
- PCB 3.1.2 signed application programming, sector verify, and reset passed on
  J-Link 69650428.
- The response-driven hardware regression tool completed two final consecutive
  `R` -> two measurements -> `I` -> stopped menu -> `F`/`Y` cycles on the
  flashed PCB 3.1.2 image. After each reconnect it first drained the firmware's
  automatic probe menu, then sent a distinct host `G` and required a second OSU
  acknowledgement plus complete CTD menu. This proves PC -> CDC -> UART1 input,
  rather than accepting the automatic internal `G` as a false pass.
- After reset, COM11 returned and E: reported FAT `Healthy`.
- Independent read-only review of ADC/Tilt `nan` paths found no blocker.
- `git diff --check` passed; its only messages concerned unrelated existing
  calibration README line-ending warnings.

## Final committed builds

Both PCB variants were rebuilt pristine from source commit `6170fd2`. The
signed binaries contain firmware identity `0.9.9O`, branch `main`, and commit
`6170fd2c`. Their generated configurations select only the intended hardware
profile.

| PCB | Flash | RAM | Result |
| --- | ---: | ---: | --- |
| 3.1.2 | 610316 / 958464 B (63.68%) | 202912 / 262144 B (77.40%) | PASS |
| 3.3.0 | 610420 / 958464 B (63.69%) | 202912 / 262144 B (77.40%) | PASS, build-only |

MCUboot `imgtool verify` passed:

```text
PCB 3.1.2: 17aa6a6d51a3688b4d6ddfb80cd5334239c9bcbf5dc9fd778b6ee26d5bf500d8
PCB 3.3.0: 2c43283282a991977597d09a910a273d1508220cd5bed2032cc73d4b1102e667
```

The final pristine PCB 3.1.2 artifact was not reflashed after packaging.
Physical USB validation used the same final source immediately before the
source commit; the later pristine rebuild has a new build timestamp and
non-deterministic RSA-PSS signature.

## Replacement 0.9.9O artifacts

The packaged files were hash-compared with their corresponding pristine build
outputs and are byte-identical:

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9O.hex
  size 1717666
  SHA256 EAB7556D7121A526401CE055B416B1CAC76C13FB0C57DE07D03D210EF58DC68E

  osu107_signed_hw3.3.0_0.9.9O.hex
  size 1717965
  SHA256 629449A794AB045D493DABEB43E764085956A7CA74D980647D3DA3169B7814B1

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9O.bin
  size 610652
  SHA256 A7E21F9B971A45F2A57E39A7A547125DD43258939EE23315800A6A76DBC1A539

  osu_m_update_hw3.3.0_0.9.9O.bin
  size 610756
  SHA256 27001DB4C21FC9CABA29AD792CB3986F4D33AF88B6B067FBC9DE854DBD17F171
```

For on-device update, select the file matching the physical PCB and rename the
destination to exactly `update/osu_m_update.bin`.

## Follow-up: automatic refresh after user calibration writes

The ordinary user menus have three one-shot operations that write the
host-visible FAT volume:

- Surface `T` interval writes `system.ini`; this path already drained/flushed
  storage and refreshed USB automatically.
- `O` Rinko Ox Adjust writes `adc_channels.ini` in both Surface and Instrument.
- `Z` Zero tilt level writes `lsm303.ini` in both Surface and Instrument.

The shared `O` and `Z` paths now propagate a `ConfigDiskWriteStatus` from the
actual config-file operation. After a write attempt with USB connected they
recheck the originating logger's stopped state, drain and flush pending appends,
release measurement storage, announce the three-second reconnect, and call
`refreshForHost()`. A failed refresh reclaims storage and remains fail-closed.
If the FAT write itself fails after MSC has been blocked, USB is still
reconnected to restore host access, while the terminal explicitly says the FAT
file was not updated.

No other ordinary one-shot menu action needs this behavior. `U` normally reads
disk and commits to NVS only; its exceptional `/config` repair branch already
auto-refreshes. `V`, clock sync, status and navigation do not write FAT.
Continuous measurement logging deliberately retains stop plus explicit `F`.
All `Ctrl+T` advanced/service paths retain their previous manual-refresh
behavior.

This follow-up is included in the code image flashed and exercised during the
Instrument USB regression. The automatic `O` and `Z` refresh branches were not
re-exercised after the final CDC lifecycle change; they use the same shared
`refreshForHost()` path that passed the Instrument regression. The packaged
artifact table above records the final pristine builds from source commit
`6170fd2`.

## Remaining validation and limitations

- Deliberately inject one ADC channel failure in both modes and confirm a
  single `nan` appears while every later column, including DATE/TIME, remains
  aligned.
- Deliberately inject an IMU read failure with Tilt configured and confirm the
  same invariant.
- Continue long-duration USB insert/stop/refresh/restart stress beyond the
  repeated automated cycles completed in this handover.
- PCB 3.3.0 remains build-only.
- The legacy USB composite device does not dynamically remove only its MSC
  interface. Protected logging uses standards-based SCSI no-medium responses
  while CDC stays active.
- Disk B spooling was considered but is not implemented. A and B share one
  QSPI peripheral and global CS configuration; safe concurrent A-host/B-local
  operation requires a new low-level dual-flash driver, bus locking, journal,
  CRC, and power-loss recovery. A Zephyr upgrade alone does not provide it.

## Diagnostic guardrail

Live `nrfjprog --readregs` or `--memrd` diagnostics can halt or disturb the CPU
long enough to drop USB. After such a read, immediately resume or reset the
device before treating a missing COM/disk as a firmware failure:

```text
nrfjprog --run --snr 69650428
nrfjprog --reset --snr 69650428
```

Do not diagnose an apparent USB hang after `--readregs` without first resuming
the MCU.

## Workspace and release safety

Do not stage unrelated calibration READMEs, calibration run folders/logs,
binder temperature-cycle files, `mvProvision/dist`, GUI settings, build
directories, or historical local artifacts. Stage the explicit OSU107 source,
this handover, changelog entry, and the final four replacement O artifacts
only. The artifact directories are ignored by default, so force-add only the
four verified hardware-labelled files.
