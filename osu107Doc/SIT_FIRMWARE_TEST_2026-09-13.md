> Superseded by the R test: see SIT_FIRMWARE_R_TEST_2026-09-13.md. The Q cleanup failure below is historical.

# SIT P-to-Q physical test — cleanup pending

Target: OSU107 SN107, PCB 3.1.2, COM11, E:. User authorized the SIT test and AppData access. No firmware source has been changed.

The actual SIT 1.4.11 single EXE read running P from the local menu, matched disk/COM by USB identity, fetched the Q manifest and notes from saiv.no, downloaded the signed image and verified its SHA-256. Config was backed up. The copy was flushed/read back before CFG/FWU. Disk/COM disappeared and returned after approximately 90 seconds. The local menu then reported Q.

The device did not remove update/osu_m_update.bin. SIT issued one additional SLP/RESET, observed the USB cycle and read Q again. The file remained, so SIT stopped **before deleting config/system.ini**. All configuration files still match their pre-update hashes. This is a successful firmware installation but not a completed updater workflow; no final success was reported.

Independent read-only inspection after the test:

```text
Menu: OSU107, SN: 107, ver-0.9.9Q.
HW: OSU-M rev-3.1.2.
FWU write lock: ACTIVE
  path=update/osu_m_update.bin
  phase=CONFIRMED_CLEANUP_PENDING
  source_on_disk_a=UNKNOWN
```

The remaining update file is the exact server Q BIN: 635580 bytes, SHA-256 `3e6840e8a3ea84564b635fbcf20e6b6ece48b86551226d14bf2f259bfb30b47c`. The on-disk system.ini still identifies P, as expected before regeneration. Do not use it as proof of running P, and do not flash again just to finish configuration cleanup.

Physical report: `analysis/runtime_test/firmware1411/physical/1789333038632105800/report.json`. Config backup also exists under `C:/Users/baard/AppData/Local/SAIV_IT/FirmwareBackups/SN107-24720-91348625`. Current state and config hashes: `analysis/runtime_test/firmware1411/physical/current_state.json`.

Before the test, an unrelated old update file existed (629744 bytes, SHA-256 `33a6655d247ac8c77655022d1a0b838f6cb0ecd5d6cb723ca570c76ce16916c8`) with FWU lock CLEAR. One reset did not remove that file. It was preserved in the project test archive. The user subsequently clarified that SIT should simply overwrite an existing update image. This is now implemented and tested, including truncating a longer old image; the complete new image is still flushed and compared before FWU.

New candidate SHA-256: `03b1758e1d368719710f2f6e7e627c6c3b45c28a944052a3c204776289e7c3ac`. The full P-to-Q attempt used the preceding candidate `8550e82f35d788b9fe64c6b378e9941b7812b8665e324c9056ffdcd6bdd4ca11`; overwrite support was added while it ran. The new candidate was separately checked against the physical unit: running Q is displayed, no newer firmware is offered, and Update device is disabled.

Outstanding: determine the firmware's required USB/disk state for CONFIRMED_CLEANUP_PENDING to finish, then complete system.ini regeneration and final preservation/version checks. No host deletion of the Q BIN or FWUCLR has been performed.
