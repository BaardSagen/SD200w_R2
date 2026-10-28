# Last opp SIT 1.4.13

Denne utgaven retter TIME/DATE og Interval som kunne åpne Convert i 1.4.12.
Flerfilkonvertering, Merge og firmwarevalg for 3.1.2 / 3.3.0 beholdes.

Last opp til `https://saiv.no/software/`:

1. `saiv_instrument_terminal_v1.4.13_oct2026.zip` – ikke pakk ut ZIP-en.
2. `readme_v1.4.13.txt`
3. `latest.json` – last opp sist og erstatt den gamle pekeren.

EXE-en inne i ZIP-en heter `saiv_instrument_terminal_v1.4.13_oct2026.exe`,
med nøyaktig samme skrivemåte som ZIP-navnet. Dette er påkrevd av oppdatereren.
Kunden trenger ingen separat DLL. Filnavnet på eksisterende installasjon beholdes.

Regresjonskontroll: `analysis/firmware1413_release_validation.json`.
Pakke- og oppdatererkontroll: `analysis/update_server1413_validation.json`.
Oppdatererprøven stopper etter utpakking og versjonsgodkjenning, før faktisk
erstatning og omstart. Ingen instrumenttilgang eller serveropplasting er utført.
Programmet er fortsatt usignert.
