SAIV Instrument Terminal 1.4.0
Released: 9 September 2026

WHAT IS NEW SINCE 1.3.6

Import and graphs
- Import converted FIELDS files and merged files into SD2 format.
- View imported data in the existing Graph, Multigraph and data list tools.
- Import to SD2 is also available from Convert.
- Keep the generated companion files together with the SD2 file.

Instrument settings
- New Interval button (Alt+I).
- New TIME/DATE button (Alt+A), using the PC clock with LT or GMT/UTC.
- With OSU107, set both the attached SD200 clock and the logger clock.
- SAIV110 Surface offers the same eleven interval choices as SD200.
- Download, Interval and TIME/DATE require a confirmed Detect result.
- Print and Setup have been repositioned; the Log button is hidden.
- Download uses Alt+D; Detect uses Alt+E.

CLOCK CORRECTION IN 1.4.0
The automatic second SD200 clock write from 1.3.9 has been removed.
The timestamp is calculated during transmission to account for transfer time.
Each clock is written once and checked independently afterwards.
This correction was physically tested on COM11 with OSU107 and SD208.
SAIV110 Surface was not physically tested for this release.

SHOULD I UPDATE?
Update if you need the new import/graph support or instrument settings.
If you use TIME/DATE in 1.3.9, 1.4.0 removes the repeated SD200 clock write.

GETTING STARTED
Extract the ZIP file and run SAIV_Instrument_Terminal_v1.4.0_Sept2026.exe.
Only the EXE needs to be distributed. Its supporting files are extracted
automatically at startup. Keep earlier releases if you need to return to them.

The online update checker is planned; it is not included in 1.4.0.
