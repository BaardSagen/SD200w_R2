SAIV Instrument Terminal 1.4.11
Released: 14 September 2026

NEW SINCE 1.4.10: DEVICE FIRMWARE UPDATE

Help > Firmware checks for firmware updates for a connected OSU107 or
SAIV110 with OSU-M hardware 3.1.2. This check runs only when you request it.
The window shows the installed version, available version and release notes.
Device firmware is separate from Help > Update software, which updates SIT.

Before updating, SIT identifies the connected device and USB disk, checks
the downloaded firmware checksum and backs up configuration on the PC.
The entire firmware file is read back from the device and compared before
the update starts. The confirmed byte count is displayed.

Automatic device communication runs in the background without filling the
terminal history. Release notes show customer information only.

The progress window shows the current step, an animated indicator and elapsed
time. Keep USB and power connected. Updating normally takes about two minutes,
followed by restart and verification. SIT waits for the same device to return,
checks its running firmware and verifies that firmware cleanup has finished.
Only config/system.ini is regenerated. Other configuration and calibration
files are retained and checked, along with settings and device identity.
The configuration backup location is shown in the window.

A manual check of the current server version also verifies the device version,
system.ini and cleanup without flashing again. No newer version is offered
when the installed firmware is already current.

The complete P-to-R update was physically tested on OSU107 SN107 / HW3.1.2,
including automatic cleanup, regenerated system.ini, retained settings and
calibration, and the final success message. SAIV110 has not been physically
tested in this release.

NEW USERS
Extract the ZIP and run the EXE. No earlier version is required.
Supporting components are embedded; no separate DLL installation is required.

EXISTING USERS
In version 1.4.1 or later, use Help > Update software > Check now.
Save your work and finish instrument operations before confirming installation.
The existing filename and location are kept, with a backup of the earlier EXE.
Versions before 1.4.1 require a manual first upgrade.

See THIRD_PARTY_NOTICES.txt for the included miniz and GSW licences.
