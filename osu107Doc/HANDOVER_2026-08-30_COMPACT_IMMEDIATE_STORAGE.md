# Handover: OSU107 0.9.9O immediate compact storage

> Follow-on USB MSC/CDC recovery and fixed-schema `nan` work is documented in
> `HANDOVER_2026-09-01_USB_MSC_CDC_NAN.md`.

Date: 2026-08-30

Branch: `main`

Target: `0.9.9O` release candidate

Firmware source commit:
`ec244261579503795d9d541e6083f6a53f059602 Simplify compact storage for 0.9.9O`

Status: implementation, host tests, independent review, both firmware builds
and signed-image verification pass. Limited user testing observed and accepted
the intended disk-ownership/refresh behavior, but the running firmware identity
was not captured and the O physical test matrix is not complete. O has not been
hardware-approved or tagged as a final release.

## Final format decision

Dynamic compact `TIMEBASE` detection is removed completely from both Surface
and Instrument storage. No startup measurement waits in RAM for an interval
pattern. Every compact measurement is queued for storage immediately.

Plain `compact` has a fixed final `TIME` field:

- rows 1-5 store the measurement time as `HH:MM:SS`;
- row 6 onward retains the final separator with an empty `TIME` value;
- `FIELDS` and every row therefore keep the same number of columns.

Example:

```text
FIELDS: COUNT;Par;OxR;TIME
1;4.26;0.29;14:37:49
2;4.26;0.29;14:37:59
3;4.25;0.29;14:38:09
4;4.26;0.29;14:38:19
5;4.26;0.29;14:38:29
6;4.25;0.29;
```

`compact+DT` has no `TIMEBASE` record either. It continues to store `DATE` and
`TIME` on every row:

```text
FIELDS: COUNT;Par;OxR;DATE;TIME
1;4.26;0.29;2026-08-30;14:37:49
```

Full-format storage and live CDC/UART measurement rows are unchanged.

## Persistence behavior

Surface writes its normal session header and `FIELDS` synchronously when the
session starts. Each measurement is then one asynchronous row append. Before
SYSTEMOFF, firmware drains the append queue and verifies that:

- no Surface append remains pending;
- no storage error is latched;
- the queued line counter equals the file-worker-confirmed line counter.

SYSTEMOFF is blocked fail-closed if any condition is false.

On Surface restore, the last newline-terminated row in the file is the
authoritative counter. Recovery supports semicolon, comma, space and tab
separators, one-value rows, and a counter-only plain-compact row when all
configured sensor reads failed and the final `TIME` field is empty.

Instrument determines `FIELDS` from its first enriched N-line and queues it
immediately before row 1. The persisted file-local counter owns recovery:
counter 1 always starts a new preamble; counter greater than 1 is a restored
file whose preamble already exists. This also covers a new session after
PASSIVE when the next Date header is delayed or missing. PASSIVE drains the
existing file queue before clearing the session path.

## FAT ownership and PC access

The storage policy is intentionally single-owner. While either Instrument or
Surface logging is active, firmware owns and locally mounts the FAT volume.
USB MSC host writes are blocked so Windows and firmware cannot modify the FAT
volume at the same time. Windows may retain a drive letter while showing the
volume as unavailable or with stale contents; this is expected during logging.

Use this handover sequence when the PC needs the current files:

1. Stop Instrument logging and/or run `SURSTOP` for Surface.
2. Wait for the active measurement, indicator blink and final queued append to
   finish.
3. Open `USBD` and run `R` (`UsbRefresh`). This flushes and safely
   re-enumerates USB mass storage for the host.
4. Wait for the volume to return. The terminal may need to select the CDC COM
   port again after re-enumeration.

Physically disconnecting and reconnecting USB is an alternative host refresh,
provided logging has first been stopped. If logging is still active, firmware
still needs the disk and host access remains blocked after reconnect.

`USBD` -> `U` is only a filesystem flush. It does not perform USB
re-enumeration or transfer the volume to the PC. The guarded flashing workflow
uses flush plus an operating-system dismount for a different purpose; that
must not be confused with the normal `USBD` -> `R` host-access workflow.

## Code and documentation

The old `src/logging/compact_timebase.hpp` tracker was deleted. Its tracker,
anchor detection, startup-row buffers, fallback flush paths, fields and
includes were removed from both loggers. Shared startup TIME formatting is in
`src/logging/compact_startup_time.hpp` and is used by both logger modes. This
helper only adds the fixed `TIME` field and its first-five-row value; it does
not infer or retain a timebase.

Current INI help, the multi-INI specification and the hardware interval-matrix
validator describe and validate the new format. The matrix validator rejects
new files containing an obsolete `TIMEBASE` record and verifies timestamps on
plain compact rows 1-5, empty TIME values after row 5, and DATE/TIME on every
`compact+DT` row.

## Verification completed

- Host C++ interval/storage test compiled with `-Wall -Wextra -Werror` and
  passed.
- Tests cover plain compact TIME rows 1, 5 and 6; one-value recovery; tab
  recovery; torn-tail rejection; and counter-only complete-row recovery.
- Python AST validation and simulated `validate_storage()` checks passed for
  six-row `compact` and two-row `compact+DT` files.
- Repository audit finds no runtime `TIMEBASE` producer, tracker, pending-row
  buffer, compact fallback flush or stale TIMEBASE-era comment. Remaining
  `TIMEBASE` text is documentation/history and a validator rejection check.
- Independent read-only review found no remaining blocker in the new flow.
- `git diff --check` passed; warnings shown by Git concern unrelated existing
  calibration README line endings.
- Both signed update images passed MCUboot `imgtool verify`.
- Both pristine images embed `0.9.9O` and Git provenance `main@ec244261`.
- Generated hardware configurations select only their intended profile:
  `CONFIG_OSUM_HW_REV_3_1_2=y` and `CONFIG_OSUM_HW_REV_3_3_0=y`, respectively.

Build results:

| PCB | Flash | RAM | Result |
| --- | ---: | ---: | --- |
| 3.1.2 | 603084 / 958464 B (62.92%) | 202912 / 262144 B (77.40%) | PASS |
| 3.3.0 | 603176 / 958464 B (62.93%) | 202912 / 262144 B (77.40%) | PASS, build-only |

Both application binaries contain the identity `0.9.9O`.

## Candidate artifacts

```text
tools/flashTool/hexfiles/program/
  osu107_signed_hw3.1.2_0.9.9O.hex
  size 1697305
  SHA256 AA27FC2A80A6F2E0400BC44934396F602003287888F73BE44C63054F4CB0E9C4

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.1.2_0.9.9O.bin
  size 603420
  SHA256 8E5A9A21A9C91557D2122ECC1771A1B240EC22D3A2CD983CA936903E869B6D97

tools/flashTool/hexfiles/program/
  osu107_signed_hw3.3.0_0.9.9O.hex
  size 1697567
  SHA256 AAC639A103B7402D0F798A0802C37B93D4492FC6AA220B05F4085D045F9AE495

tools/flashTool/hexfiles/updateBin/
  osu_m_update_hw3.3.0_0.9.9O.bin
  size 603512
  SHA256 0494085740F403BBC6A5671FB74D91AABBC4C72EFDD002FDE01A9A5E12E5C443
```

MCUboot verification digests:

```text
PCB 3.1.2: e9b13213fe2d231770016b1b546a9087baf7128ad14cbbef4535670408e41e76
PCB 3.3.0: 9ba926bf52ff5781f45ffb3f18255de2cfffc4ce10ed809e565ba114a2204f3c
```

The packaged files were hash-compared with their corresponding build outputs.
For on-device FWU, select the correct PCB file and rename the destination to
exactly `update/osu_m_update.bin`.

Repository artifact policy keeps only this newest four-file O set tracked on
`main`. All older packaged HEX/BIN files are removed from the current Git tree
but remain recoverable from repository history. The artifact directories are
ignored by default; future releases must force-add only their verified current
hardware-labelled set.

## Required physical test before release

1. Confirm that the PCB 3.1.2 device reports `VER=0.9.9O` and
   `main@ec244261`; if not, flash the O candidate with the guarded app-only
   procedure while logging is stopped and the OSU FAT volume is safely
   dismounted.
2. In plain `compact`, stop after only 1-3 measurements and confirm every row
   is stored immediately with no `TIMEBASE` line.
3. Record at least six plain compact rows and confirm TIME on rows 1-5 and an
   empty final TIME field from row 6.
4. Test a SYSTEMOFF interval: Instrument greater than 10 seconds and/or Surface
   at least 30 seconds. Unplug USB long enough for multiple wakes, reconnect,
   and confirm contiguous stored counters without another `FIELDS` line.
5. Run a short `compact+DT` session and confirm DATE/TIME on every stored row.
6. Stop logging and use `USBD` -> `R`; confirm the current files become
   available to the PC only after this handover (or a stopped-state USB
   disconnect/reconnect).
7. Eject/dismount safely and run a read-only filesystem check.

Do not release or push O as hardware-validated until these checks pass.

## Existing non-blocking limitations

- Instrument's general measurement queue has an existing 512-byte per-message
  limit and does not report queue-full drops through `ILogSink::enqueue()`.
- Instrument PASSIVE uses the existing two-second drain timeout and does not
  act on a timeout result.
- If Surface cannot read the log tail during restore, it falls back to the
  retained/persisted counter.

## Workspace safety

Do not stage unrelated calibration files, binder temperature-cycle logs,
historical firmware artifacts, `mvProvision/dist`, GUI settings or adjacent
Zephyr SDK changes. Avoid `git add .`; stage only the explicit O source,
documentation and four O candidate artifacts.
