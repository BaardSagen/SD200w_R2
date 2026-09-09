# SAIV IT 1.4.4 – Quick guide

Leveranse: **SAIV_Instrument_Terminal_v1.4.4_Sept2026.exe**. Kunden trenger bare denne EXE-filen. Tidligere leveranser er beholdt.

## Bruk

Velg **Help > Quick guide...**. Guiden er på engelsk, som resten av SIT, og bruker vanlige Windows-kontroller og samme vindusstil som programmets øvrige tilleggsdialoger. Den er innebygd og trenger verken internett eller tilkoblet instrument.

Velg blant ni korte emner: Start here, Detect and terminal, Download and save text, Open and import files, Convert and export, Merge files, Lists, graphs and print, Interval and TIME/DATE samt Setup and Help. Emnene beskriver SITs faktiske knapper, menyer og SD2/CSV/TXT-arbeidsflyt. Studio er ikke fasit for denne guiden.

Piltastene velger emne, Tab flytter fokus, og Esc eller Close lukker guiden. Vinduet kan endres i størrelse. Lukk guiden for å arbeide videre i SIT.

## Kontroll og bygg

Den ferdige enkelt-EXE-en er startet fra en egen testmappe med mellomrom og norske tegn, uten administratorrettigheter. Alle ni emner, tastaturvalg, Esc, Close, vinduskrysset, gjenåpning, minimumsstørrelse og eksisterende Help > Update software er kontrollert i kjørende SIT. Guiden er også kontrollert visuelt. Ingen instrumentkommandoer eller oppdateringsforespørsler ble sendt under testene.

GUI-rapport: `analysis/runtime_test/guide144/gui_validation.json`. Samlet leveransekontroll: `analysis/guide144_release_validation.json`. Byggmanifest: `analysis/single_exe_144_manifest.json`.

Kilde: `sit_import/quick_guide.inc`, med menytilkobling i `sit_import/update_ui.inc`. Bygg: `analysis/build_single_exe_144.py`, med `C:\MinGW\bin` i PATH. Grunnlaget er hashbundet 1.4.3-runtime. Hele runtime-filen er sammenlignet etter de avgrensede endringene i About/versjonsressurser, DLL-navn og PE-sjekksum. Installerhjelperen er identisk med forrige versjon. Ingen endring i instrument-, beregnings-, import- eller konverteringslogikk.

1.4.3-modulkilden er bevart i `analysis/reference/sit_import_v143`; det historiske 1.4.3-byggskriptet bruker nå dette arkivet. Ingen serveropplasting eller Git-push er gjort.

En visuell gjennomgang av faktisk instrumentbruk er mulig, men er uttrykkelig utsatt til instrumenter er tilkoblet. Denne leveransen inneholder tekstguiden. GUI-testbildene er intern kontroll av hjelpevinduet, ikke den utsatte gjennomgangen.
