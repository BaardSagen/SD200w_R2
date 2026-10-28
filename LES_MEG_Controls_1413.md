# SIT 1.4.13 – TIME/DATE og Interval rettet

28. oktober 2026. Nyeste leveranse:
`SAIV_Instrument_Terminal_v1.4.13_Oct2026.exe`.
Brukeren ba uttrykkelig om nytt versjonsnummer 1.4.13 for denne rettelsen.

Flerfilendringen i 1.4.12 omdirigerte den delte Delphi-klikkrutinen til
Convert. Merge var håndtert særskilt, men Interval og TIME/DATE ble også
sendt til Convert. Rutinen sender nå merkede knapper til den eksisterende
dispatcher-kjeden; Convert beholder flerfilflyten. Beregnings-, klokke-,
intervall-, firmware- og serieprotokoller er uendret.

Begge innstillingsknappene er testet i riktig dialog for SD200, OSU107 og
SAIV110. Det er også kontrollert at de er sperret uten Detect og etter
portbytte, og at avbrudd gir hovedvinduet tilbake. Convert-knapp og File-meny,
enkeltfil, flere filer, Merge og firmware-/programoppdateringsvindu er testet.
Eksportene er byteidentiske med bevarte referanseeksporter.

Testene bruker egne runtime-kopier fra leveransen på privat skrivebord,
minnestubber for registeret og sperret fysisk serieportåpning. Godkjent Detect
simuleres bare i testprosessens minne. Ingen faktisk klokke-/intervallskriving
eller firmwareoppdatering er utført. Den nye maskinkoden er også testet ved
normal og flyttet innlastingsadresse med bevarte registre og stakk.

Bygg: `analysis/build_single_exe_1413.py`, modul `SIT_Import155.dll`.
Patch: `analysis/patch_dispatch1413.py`.
GUI-regresjon: `analysis/check_controls1413.py`.
Maskinkodetest: `analysis/test_dispatch1413.py`.
Samlet byggbundet kontroll: `analysis/validate_controls1413.py` og
`analysis/firmware1413_release_validation.json`.

Brukeren krevde at disse knappene alltid testes samlet etter endringer i
knapper, menyer eller delte klikkrutiner. Regelen står i AGENTS.md.
Tidligere tester av eldre versjoner erstatter ikke ny leveransekontroll.

Serverpakke: `update_server/LAST_OPP_1.4.13.md`. ZIP-oppføringen bruker små
bokstaver nøyaktig som forventet av eksisterende oppdaterere.
Programmet er fortsatt usignert. Ingen serveropplasting, commit eller push.
