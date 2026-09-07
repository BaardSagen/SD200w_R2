# Handover: OSU107 0.9.9N interval, power, CALSYS and FAT ownership

Date: 2026-08-30

Branch: `intervall_test`

Release: `0.9.9N`

Source commits:

- `00936a5 Prepare OSU107 firmware 0.9.9N`
- `6a921a9 Make MCUboot versioning reproducible`

The commit containing this handover and the four packaged 0.9.9N artifacts is
the release commit. The release branch is fast-forwarded into `main`; both
branches are pushed after the validation recorded below.

Final identity read from SN107:

```text
SW: SAIV110 ver-0.9.9N
HW: OSU-M rev-3.1.2
Git: intervall_test@6a921a90
```

Hardware used:

- OSU107 SN107, PCB 3.1.2
- SAIV CTD SN1456
- OSU107 USB CDC COM11
- J-Link CDC COM6
- J-Link probe serial 69650428
- OSU FAT volume E:

## Result

The interval, power, CALSYS and FAT-ownership work is accepted for release.

The main behavioral changes are:

- `sensor_preheat_seconds` defaults to 2.0 s and is parsed strictly.
- P0.4 external-sensor power and P0.1 analog-front-end power start together.
- Preheat is separate from acquisition time.
- CALSYS runs once per logical Instrument or Surface session, not once per
  SYSTEMOFF reboot.
- ADS1263 OFCAL is persisted and restored after PWDN and SYSTEMOFF.
- Surface uses one immutable configuration snapshot for the entire session.
- Surface start is idempotent: starting an already-running logger does not
  re-anchor cadence or inject another measurement.
- Surface queued writes use generation ownership, explicit append draining and
  a worker-idle acknowledgement before stop, restart or SYSTEMOFF.
- Critical SYSTEMOFF paths stop and quiesce Surface before storage shutdown.
- FAT ownership is serialized between firmware and USB MSC.
- Host writes are blocked while firmware owns the disk and reopen only after
  the explicit USB refresh operation.
- FAT auto-format-on-mount is disabled. Mount and health failures fail closed,
  so firmware cannot silently replace a damaged customer volume.
- The guarded `flash-app.ps1` app-only path uses direct `nrfjprog`
  program/verify followed by exactly one explicit system reset. The sysbuild
  West runner is not used by that path. GUI flashing continues to use J-Link
  Commander.
- CLI and GUI flashing validate the exact probe, stopped/flushed measurements,
  removal of the OSU disk and continued OSU107 CDC/VBUS presence.

## Physical observations on development version 0.9.9M

These are user-observed electrical tests on SN107. They must not be represented
as measurements made on the final N binary.

With `sensor_preheat_seconds=2.000000` and
`startup_calsys_enable=1`, the user observed:

- approximately 50 uA between measurements;
- an approximately 2 s external-sensor power window;
- correct operation with OSU USB connected;
- correct operation after USB was disconnected;
- correct operation after USB was connected again;
- removal of the former roughly 3 s post-indicator CALSYS tail.

The accepted Instrument file was:

```text
E:\instrument\2026\08\2026_08_29_14-37-47_F.txt
```

It contained 43 complete rows, N1-N43. The stable USB-off section N17-N35
contained 19 rows with all 18 gaps exactly 10 s. The post-replug section
N37-N43 contained seven rows with all six gaps exactly 10 s. Every row had the
expected CTD, Par, OxR and Tilt fields.

Configuration was re-read as:

```ini
startup_calsys_enable=1
sensor_preheat_seconds=2.000000
gnd_ref_ch=6
```

This demonstrated that CALSYS belongs to the logical logging session while
preheat still occurs for every measurement.

## Final 0.9.9N device verification

The final N image was flashed to SN107 using the guarded app-only procedure.
Preflight passed, direct `nrfjprog` program and verify passed, and the script
performed one system reset. COM11 and E: returned after reset.

Final Surface test:

```text
Start requested:          19:51:01
Repeated start command:   19:51:06 -> surface already running
Log file:
E:\surface\2026\08\2026_08_30_19-51-03_F.txt

S1  19:51:07
S2  19:51:37
S3  19:52:07
S4  19:52:37
Stop completed:           19:52:40
```

All three row gaps were exactly 30 s. The repeated start neither generated an
extra row nor changed the established cadence. The first row included the
session's one-time CALSYS work; later rows stayed on the exact 30 s phase.

While Surface owned the disk, a host write remained blocked and no partial
file was created. After `SURSTOP`, `USBD/R` and USB re-enumeration, host
write/read/flush/delete passed.

Final read-only CHKDSK result:

```text
Filesystem clean
159 files
460800 bytes in files
7858176 bytes free
```

Before the final Surface file was created, the clean baseline was:

```text
158 files
458752 bytes in files
7862272 bytes free
```

The count and allocation changes are exactly consistent with the new Surface
file. The device was left with Surface stopped, direct Instrument
communication reactivated, COM11 present and E: mounted.

The final N validation covers firmware identity, guarded flashing, Surface
cadence, repeated-start behavior, pending-write draining, MSC write blocking,
USB refresh/reopen and FAT consistency. The user was no longer present to
physically disconnect USB or measure current on the final N binary; the
50 uA, 2 s and physical USB-out/in observations above were performed on M.

## Builds and tests

Both hardware configurations were rebuilt pristine from committed source.

| PCB | Flash | RAM | Result |
| --- | ---: | ---: | --- |
| 3.1.2 | 605820 / 958464 B (63.21%) | 203168 / 262144 B (77.50%) | PASS, hardware tested |
| 3.3.0 | 605908 / 958464 B (63.22%) | 203168 / 262144 B (77.50%) | PASS, build-only |

Additional checks passed:

- host interval/preheat policy test;
- MCUboot `imgtool verify` of both packaged update BIN signatures;
- PowerShell parsing of the CLI flashing scripts;
- Python AST and probe-field validation for the flashing GUI;
- unsafe recovery still requiring explicit stopped/flushed confirmation;
- hardware-revision configuration checks;
- generated MSC and flash-disk override symbol checks;
- clean Zephyr-generated override equivalence audit;
- independent review of the Surface generation/idle barrier;
- independent review of the immutable Surface configuration snapshot;
- `git diff --check`.

Generated override hashes were identical for both hardware profiles:

```text
MSC generated source:
4C7A05FD7FF72F9E2BF65F2DE794C83E6D7B513CB803EDC545139A10268D7A39

Flash-disk generated source:
C75A4D18C4754095E14A620C4CB4E213B92EF38435BAAF6BFEDB449965E81C9D
```

## Release artifacts

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9N.hex
  size 1705004
  SHA256 7D00AC76EC5E3EB2DC5138CEF64F356BD1D3316A4641FE32182037C89A872141

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9N.bin
  size 606156
  SHA256 05DBA04E8597587B3A60C4E45A6E0842FB13BA88E57B84A6405451310983EAD5

tools/flashTool/hexfiles/program/
  osu107_signed_hw3.3.0_0.9.9N.hex
  size 1705275
  SHA256 597D5B1B3BD5CF68F58BB082E3445E7DB3AE3C5B7FD230F5FE291C6AA0C2D261

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.3.0_0.9.9N.bin
  size 606244
  SHA256 C0BFFBCA46B31065CED31C5EDB8941F065F98B6ACBDE8456F385CBEBD755D73E
```

The packaged PCB 3.1.2 HEX/BIN match the exact signed files used for the final
program/verify operation. RSA-PSS signing is intentionally non-deterministic,
so re-signing the same payload produces a different valid signature and file
hash; record and distribute the packaged files above.

For an on-device firmware update, select the file for the physical PCB and
remove its hardware/version suffix. The destination name must be exactly
`NAND:\update\osu_m_update.bin`, matching the firmware's default FWU path.

The reproducible MCUboot image is identical for both builds:

```text
size 104327
SHA256 13B636711AF7C2897F20A5AD37440BFB1D08E2CB4EFD4A86F1DA3F58F36AF91E
banner: MCUboot v2.1.0-34-gfb2cf0ec3da3
```

Commit `6a921a9` adds the MCUboot repository to Git safe-directory setup during
build. Without it, a pristine build generated an empty MCUboot build version
and a different binary.

## Flash-test incidents and recovery

Two mounted-volume incidents occurred during development. Both are recorded
here to preserve the storage history.

### Diagnostic West-runner incident

A diagnostic attempted to substitute a mock `nrfjprog` command to count reset
operations. Windows resolved the real executable instead, and `west flash`
began its sector erase while E: was still mounted. Surface was stopped and no
firmware FAT write was active. The operation was interrupted immediately, but
the application was partially erased and COM/MSC disappeared.

E: was then dismounted and the application was recovered with program, verify
and system reset. COM11 and E: returned. CHKDSK was clean and the
file/allocation counts were unchanged.

This exposed that the West sysbuild runner appends a pin reset even when
`--no-reset` is supplied. `flash-app.ps1` was consequently changed to call
`nrfjprog` directly and perform exactly one explicit reset.

### Unsafe-override negative-test incident

A later negative test invoked:

```powershell
.\flash-app.ps1 -HardwareRevision 3.1.2 -ProbeSerial 69650428 `
  -ConfirmMeasurementsStoppedAndFlushed -AllowUnsafeMountedOsuDisk
```

The assumption was that another confirmation gate would reject it. The actual
contract treats `-AllowUnsafeMountedOsuDisk`, together with the stop/flush
confirmation, as the deliberate recovery override. It therefore programmed
and verified 0.9.9N while E: remained mounted.

Surface was already stopped and no logger file was open or changed. Program,
verify and reset completed successfully. COM11 and E: returned, firmware reported
0.9.9N at `6a921a90`, and CHKDSK was clean with the unchanged baseline of
158 files and 458752 bytes in files.

The correct safe sequence was then repeated:

1. `SURSTOP`
2. `USBD/U`
3. verify the FAT volume and flush completion
4. dismount only E: with `mountvol E:\ /p`
5. verify E: is absent while COM11 remains present
6. run guarded `flash-app.ps1` without the unsafe override
7. allow direct program/verify and one system reset
8. verify COM11/E: return
9. run read-only CHKDSK

`mountvol /p` printed `Ingen tilgang` and returned exit code 1 on this host,
but the required postcondition was independently verified: E: was absent and
COM11 remained live before flashing.

No corruption, missing files or torn rows were found after either incident.

## Safe app-flash procedure

Stop both logging paths, wait for the active measurement and final append, run
`USBD/U`, eject/dismount only the verified OSU volume, and keep USB
CDC/VBUS connected. Then use:

```powershell
.\flash-app.ps1 -HardwareRevision 3.1.2 -ProbeSerial 69650428 `
  -ConfirmMeasurementsStoppedAndFlushed
```

Do not use `west flash` for this release. Do not use
`-AllowUnsafeMountedOsuDisk` in normal operation; it is a recovery-only
override and intentionally bypasses host-state checks.

## Disk-health behavior

Firmware checks mount and filesystem health and fails closed. It can detect and
report failures and will not auto-format a failed volume. This is useful
protection, but it is not a replacement for a host-side offline consistency
check such as read-only CHKDSK after abnormal power loss or flashing.

## Remaining limitations

- PCB 3.3.0 is pristine-build verified but not hardware tested.
- Final N was not physically measured at 50 uA and was not tested with USB
  physically unplugged/replugged after the final build. Those physical
  observations were accepted on development M using the same 2 s power/CALSYS
  behavior.
- The pre-existing TCA shadow is updated before a hardware write and is not
  rolled back on a real I2C write failure. This is medium-priority hardening;
  no such failure was observed in release testing.
- Legacy raw staged-configuration readers outside Surface remain unchanged.
  Surface itself uses an immutable session snapshot.

## Workspace safety

Only the OSU107 source, release documentation and four 0.9.9N release artifacts
belong to this release.

Do not stage unrelated calibration files, binder temperature-cycle logs,
historical 0.9.8 flash artifacts, `mvProvision/dist`, GUI settings or adjacent
Zephyr SDK changes. Avoid `git add .`.
