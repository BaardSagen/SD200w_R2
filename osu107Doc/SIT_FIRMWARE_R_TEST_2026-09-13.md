# SIT P-to-R physical test: final device verified

OSU107 SN107, HW3.1.2, COM11 is now running **0.9.9R**. USB stayed connected throughout the test. No firmware source was changed.

The server latest.json, readme.txt and R BIN all returned HTTP200 and matched the local package. BIN: **635648 bytes**, SHA-256 `d557327dae4af7bc90ef2555c800184a6cc08296622cada0f6fc347d30af24a6`.

The actual SIT single EXE verified running P, backed up config, copied/flushed/read back the complete BIN and sent CFG/FWU. The matching disk/COM returned after about 92.5 seconds. R removed its own update file and FWUST reported CLEAR. SIT backed up config again, deleted only system.ini and sent SLP/RESET.

The first run stopped at final verification because SIT sent CFG from direct mode after this last reset. No false success was reported. Fixed: the FWUST check now explicitly enters the local menu. A manual Check firmware on an already installed server version now verifies the current INI identity/version and firmware cleanup without flashing, resetting or deleting anything.

Independent final checks and the corrected EXE's manual check passed:

- Fresh local menu and VER: OSU107 SN107 / HW3.1.2 / 0.9.9R.
- Regenerated config/system.ini: sw_ver=0.9.9R.
- FWUST: CLEAR. update folder: empty.
- adc_core.ini, adc_channels.ini and lsm303.ini: byte-identical to pre-update backup.
- Every INI key/value other than sw_ver is unchanged, including serial, mode and settings.

The corrected EXE reports: `Verified: device version, system.ini and firmware cleanup.` It does not offer another update for the same R version. The animated indicator, elapsed time, USB warning and exact byte count were visually checked during the real flash; two captured frames confirm animation.

Reports:

- `analysis/firmware1411_validation.json`: final build hash, tests, limitations.
- `analysis/runtime_test/firmware1411/physical/1789335812151538500/report.json`: original P-to-R GUI run, including the final-check error.
- Same directory: `final_disk_verification.json`, `config_before`, `config_after`, progress screenshots.
- `analysis/runtime_test/firmware1411/physical/1789336073723397700/report.json`: corrected EXE manual final verification.
- `analysis/runtime_test/firmware1411/physical/inspect-after-*`: independent VER/FWUST transcript.

Backup: `C:/Users/baard/AppData/Local/SAIV_IT/FirmwareBackups/SN107-14304-94123937`.

Final acceptance retest, completed 14 September 2026: the user restored P, and the unchanged final EXE completed the full P-to-R cycle, including the final Firmware update successful dialog. VER/INI R, FWUST CLEAR, empty update folder, unchanged other configuration files and every other INI value were verified. No additional cleanup reset or manual intervention was needed. Report: `analysis/runtime_test/firmware1411/physical/1789336734610481300/report.json`; acceptance and screenshots are in the same directory. Backup: `C:/Users/baard/AppData/Local/SAIV_IT/FirmwareBackups/SN107-3596-95045359`. Final EXE SHA-256: `e92f36b0bb26b90e36296ea1c9066fe641539c76eaf85f56352c970047857dff`. SAIV110 has not been physically tested. All owned test processes were closed and COM11 released.
