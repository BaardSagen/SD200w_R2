SAIV110 / OSU107 firmware 0.9.9R
Hardware: OSU-M 3.1.2
Release date: 2026-09-13

Changes from 0.9.9Q to 0.9.9R
---------------------------
- Fixed firmware-update cleanup with the USB cable continuously connected.
  When an update lock is stored, USB enumeration waits until boot confirmation
  and the cleanup attempt finish. Windows receives disk access afterwards.
- Removes the update source file and clears the persistent FWU lock after a
  successful confirmed update. Also handles CONFIRMED_CLEANUP_PENDING left by Q.
- Keeps the existing exclusive disk-access protection. Firmware does not delete
  files while Windows owns the disk. If cleanup fails, the lock remains and
  USB diagnostics become available; a later reboot can retry.
- Preserves serial number, operating mode, settings and calibration. This
  release does not change ADC sampling or the N-line/S-line calibration path.

Earlier changes: 0.9.9Q (2026-09-07)
----------------------------------
- Local logger clock entry with X and LT/GMT label selection.
- Numeric input echo for instrument oxygen calibration and coefficient menus,
  and streaming progress during instrument self-test.
- Configuration update with U while the external instrument is asleep/absent.
- Rejects configuration with Instrument and Surface enabled simultaneously.

Earlier changes: 0.9.9P (2026-09-03)
----------------------------------
- Improved automatic air-pressure setting after external Mag-Key starts,
  range-change handling, UART framing and shared disk access.

Updating
--------
Use the BIN for the correct hardware revision. Back up configuration and keep
USB and power connected until the updater has finished verifying the device.
After reboot, check the running version with VER, FWUST must report CLEAR,
and update/osu_m_update.bin must be absent before completing the update.
To refresh the software identity in config/system.ini, delete only that file
and reboot through Ctrl+T, SLP, RESET. Retain other configuration files and
verify serial number, operating mode and calibration afterwards.
If cleanup remains pending, retain the backup and report the FWUST status.
