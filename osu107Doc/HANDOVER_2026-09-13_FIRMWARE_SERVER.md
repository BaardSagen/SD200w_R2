# Firmware server package and P-to-Q update test

The current offered release remains 0.9.9Q. No firmware was rebuilt for this
task. Metadata and user-facing release notes were generated from the existing
signed artifacts and CHANGELOG / release handovers.

## Files for the updater agent

Local server staging directory:
`C:/cprojects/delphi/sd200w_r2/firmware_server/osu107_saiv110/hw_3-1-2/`

- `latest.json`
- `README.txt`
- `osu_m_update_hw3.1.2_0.9.9q.bin`

Q SHA-256: `3e6840e8a3ea84564b635fbcf20e6b6ece48b86551226d14bf2f259bfb30b47c`

The lowercase filename in the manifest matches the staged BIN exactly, including
case for a case-sensitive web server. Product firmware identifies itself as
0.9.9Q; the manifest uses 0.9.9q, matching the supplied schema. The readme URL is
`https://saiv.no/software/firmware/osu107_saiv110/hw_3-1-2/README.txt`.
The BIN is resolved relative to the manifest's directory. No online upload was
performed. Treat the manifest as the current release; do not put the archived
P manifest over the Q manifest when testing an upgrade.

Separate versioned reference packages, each with the same three-file layout:
`tools/flashTool/hexfiles/server/hw_3-1-2/0.9.9P/` and `0.9.9Q/`.

P SHA-256: `1a873f645e7e45252b0c03b577c5f93ef8b7715450c1f6fc29abb481bf093917`

## Device and configuration

Target: OSU107 SN107, PCB 3.1.2, COM11. J-Link serial 69650428, CDC COM6.
Before flashing, live VER confirmed Q, build Sep 07 2026 17:06:46,
main@602becb1. Its existing system.ini still said P. This demonstrates why the
updater must verify the running firmware, not rely solely on the disk file.
Configuration backup and serial transcript are under
`../calibrate/SN107/firmware_p_update_test_20260913/` relative to osu107.
Device-side USB flush reported OK.

P flashing is complete and verified. Reconnecting J-Link USB fixed the initial
USB out-of-sync error; the user then connected the missing SWD cable to the
board. A full flash backup was taken, the stopped device was flushed, its E:
volume unmounted, and the standard safety preflight passed with SN107 CDC live.
The archived P application HEX was programmed with sector erase and verified.
Full readback matched P, and every flash byte outside the programmed application
pages matched the backup, including bootloader and NVS. E: was restored.

Following the user's explicit instruction, only `E:/config/system.ini` was
deleted, then the board rebooted through Ctrl+T -> SLP -> RESET. Final live VER
reports P, build Sep 03 2026 19:49:32, main@602becb1, PCB 3.1.2. The regenerated
system.ini also reports P and serial 107. Instrument/Surface mode enables match
the original configuration. adc_core.ini and adc_channels.ini match their
original backups byte-for-byte. COM11 is available and the script closed it.

The supplied README template described deleting the entire config folder. The
user clarified that config/system.ini must be deleted and regenerated with the
SLP RESET sequence. That narrower procedure was tested successfully here after
the P flash. Preserve other config files, serial and calibration. The updater
agent must separately test this sequence after a server-driven P-to-Q update;
that update itself has not been run here. Do not use stale system.ini alone as
proof of the installed version.

## Future deliveries

Write `firmware-release-notes/<version>.txt`, then export the signed build with
`tools/sync-flashTool-files.ps1`. It now invokes
`tools/prepare-firmware-release.ps1` and creates a versioned three-file server
package. Existing BINs can be packaged directly with that helper. The helper
checks product version text, refuses incomplete notes and refuses overwriting a
same-named BIN with different bytes. SHA-256 is calculated from the actual BIN.
Keep the hardware profile and signing verification in the build workflow;
metadata generation alone is not signature or hardware-compatibility validation.

Validation: both PowerShell files parsed; P/Q package hashes and file counts
checked; mismatched P BIN / Q metadata rejected before output. Q artifact hash
matches the published local release handover. The original supplied templates
were backed up with the device test records.
