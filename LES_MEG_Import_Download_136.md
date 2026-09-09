# SAIV Instrument Terminal 1.3.6

Kunden trenger bare `SAIV_Instrument_Terminal_v1.3.6_Sept2026.exe`. Innebygd runtime og DLL settes opp automatisk uten administratorrettigheter, som i 1.3.5. Tidligere leveranser er beholdt.

- File > Import CSV/TXT er den gjenopprettede originale Import ASCII-funksjonen. Den leser eldre instrumenttekst og lager native SD2 med tilhorende filer. Convert CSV/TXT beholdes separat, og viser en henvisning til Import for eldre instrumenttekst.
- Import av `data/26090606_18.11.51.txt` gir 43 maalinger. SD2, RF2, OX2 og OP2 er byteidentiske med originalimporten. Dette er ikke generell CSV-import: `_C` og `_merged` til native format er senere arbeid.
- Download husker bekreftet OSU107/SAIV110 fra Autodetect for samme COM-port. Logger-Download hopper over leting etter gamle CTD/Burst-headere i terminalhistorikken og sender ikke loggerens svarlinjer til CTD-parseren. Eksisterende F / Refresh disk Y/N / Y og bekreftelse beholdes. En ny bekreftet instrumentseleksjon erstatter identiteten; Cancel beholder den forrige. Native SD200- og Log-grenene beholdes.
- Convert normaliserer PAR til Par og OXR til OxR i FIELDS og Full-tekst, og bruker de samme beregningene og tidligere kolonnevalgene. OX er fortsatt et eget felt. Dupliserte aliaser avvises.

Verifisert: 43 originale maalinger og alle fire native filer mot originalimport, separat Import/Convert i faktisk enkelt-EXE, 53 alias-/beregningskontroller, 35 Fahrenheit-kontroller, 263 preset-kontroller, 2054 GUI-verdikontroller, 46 native hook-kontroller med flyttet baseadresse og 15 refresh/protokolltester med simulert serieport. Confirmed OSU107 gjennomga success/error/timeout-handshake. Ingen fysisk instrumenttest i denne leveransen. CTD-formelbytes 0x10A000-0x10CFFF er identiske med byggegrunnlaget 1.3.2.

Bygg: `analysis/build_single_exe_136.py`, `analysis/patch_native136.py`, `sit_import/native136.s`, `sit_import/` og `sit_single/`. Manifest: `analysis/single_exe_136_manifest.json`. Historisk 1.3.5-kilde er arkivert i `analysis/reference/sit_import_v135` og `analysis/reference/sit_single_v135`; 1.3.5-bygget peker dit.

SHA256 enkelt-EXE: `9205b23987ada6cac4bac3e7d0e5a65b90db0c1d8f44c2c030c9102c23de4129`.

Arbeid paa main. Den tidligere prototypen paa feature/import-all-fields er fortsatt satt paa pause. Ingen GitHub-push.
