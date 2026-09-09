# SAIV IT 1.4.2 - test av oppdatering fra 1.4.1

1.4.2 har samme funksjoner som 1.4.1. Bare versjonsmerking er endret; instrumentkode, formler, grafer og oppdateringshjelper er beholdt. Den fullstendige EXE-en fungerer ogsaa direkte for nye brukere, uten en eldre installasjon.

Last opp til https://saiv.no/software/:
1. update_server/SAIV_Instrument_Terminal_v1.4.2_Sept2026.zip
2. update_server/README_v1.4.2.txt
3. update_server/latest.json (sist)

For aa teste oppgradering: start den bevarte 1.4.1-EXE-en, velg Help > Update software > Check now, les README og velg Install update. Den installerte filen beholder sitt gamle filnavn og plassering. Kontroller etter omstart at Help > Update software viser 1.4.2; filnavnet kan fortsatt inneholde 1.4.1. Gammel fil ligger som .previous-...bak.

Nye brukere kan laste ned ZIP-en, pakke den ut og starte 1.4.2-EXE-en direkte. De trenger ikke installere 1.4.1 foerst.

Bygg: analysis/build_single_exe_142.py. Dette er et versjonsbegrenset bygg fra bevarte 1.4.1-runtime/DLL med SHA-kontroll. Helperen er byteidentisk. Versjonsstrengene i DLL og runtime/launcher-ressursene er oppdatert. Pakking: analysis/prepare_update_server_142.py. Kontroller inkluderer faktisk enkelt-EXE oppstart og versjonsvisning, samt installasjon fra en isolert 1.4.1-kopi med dens originale oppdateringshjelper. Ingen instrumentkommandoer eller serverendring er gjort. Branch update; ingen push.
