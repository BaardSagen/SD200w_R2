# SAIV IT 1.4.5 – instrumentikon i About

Leveranse: **SAIV_Instrument_Terminal_v1.4.5_Sept2026.exe**. Kunden trenger bare denne EXE-filen.

Help > About bruker nå instrumentikonet fra `icon/ctd_in_Cage.ico`, som også brukes av programmet og Instrument-knappen. Det gamle olivengrønne instrumentbildet er erstattet. Tekst, krediteringer og knapper i About er beholdt. Quick guide fra 1.4.4 er med videre.

Ikonets eksisterende 64 × 64-pikslers bilde er kodet som et klassisk Windows DIB-ikon fordi den gamle Delphi-visningen ikke håndterer PNG-bildene i ICO-filen riktig. Pikselverdier og gjennomsiktighet er kontrollert uendret ved dekoding. Bildet vises uten Delphi-sentrering, som ellers bruker feil systemikonstørrelse og klipper 64-pikslersbildet.

Bygg: `analysis/build_single_exe_145.py` med `C:\MinGW\bin` i PATH. About-ressursen endres av `analysis/patch_about_icon145.py`. Kilden er hashbundet 1.4.4-runtime; tidligere EXE-er er beholdt. 1.4.4-modulkilden er arkivert i `analysis/reference/sit_import_v144`, og det historiske 1.4.4-byggskriptet bruker arkivet. Bare oppgitt oppdateringsversjon er endret i modulen. Instrument- og datalogikk samt installerhjelper er bevart.

Den ferdige enkelt-EXE-en er kontrollert i kjørende SIT: About åpner og lukkes, det nye ikonet vises helt, tekst og knapper er synlige, Quick guide åpner, og Update software viser versjon 1.4.5. Ingen instrumentkommandoer eller oppdateringshenting er utført. Testbildet er intern kontroll av About, ikke den utsatte visuelle gjennomgangen av instrumentbruk.

Kontroller: `analysis/about_icon145_patch_validation.json`, `analysis/runtime_test/about145/gui_validation.json` og `analysis/about145_release_validation.json`. Byggmanifest: `analysis/single_exe_145_manifest.json`. Ingen serveropplasting eller Git-push.
