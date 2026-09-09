# SAIV Studio 0.3.0 – 10. september 2026

Kjør `SAIV_Studio_v0.3.0_Sept2026.exe`. Dette er et nytt, selvstendig Windows x64-program. Original SIT 1.4.3 og tidligere leveranser er beholdt.

Starter rett i terminalen med moderne utseende og Autodetect, Download, Convert, Merge, Interval, TIME/DATE, Print, Save og Setup. Skriv direkte i terminalen. Dialogtekst og målevisninger sender ikke tegn til instrumentet.

Nye målinger lagres som CSV med alle kolonner, tidsstempler og måleopplysninger. Eksisterende SD2 kan åpnes når RF2 og eventuelle OX2/OP2/SF2 følger med. Nye data trenger ikke SD2.

Convert/Merge bruker prosjektets SIT-moduler og dokumenterte SIT-formler. Målevisningen har tabell, parvise tidsgrafer/profiler, T-S og Multigraph. Dataverktøy lager et nytt datasett.

1164 automatiske kjerne-, kompatibilitets- og innstillingsprotokollkontroller består. GUI-testen kontrollerer direkte tegn/kontrolltegn, Setup-fokus, konvertering av 79 rader, Fahrenheit med original Celsius, CSV-lagring og grafer. Rapport: `analysis/studio030_release_validation.json`. Ingen fysisk instrumentport eller skriver ble brukt i denne testen.

Fysisk instrumentakseptanse av Studio gjenstår. Full funksjonslikhet med SIT, alle spesialeksporter, kalibrering/firmware, grafutskrift og Mac-/Linux-utgaver er ikke ferdige.

Kilde og bygg: `saiv-studio/`, kjør `build.cmd`. Program/lisenser/dokumentasjon i `saiv-studio/dist/SAIVStudio-0.3.0-Windows-x64.zip`. Detaljert funksjonsstatus: `saiv-studio/docs/FUNKSJONSSTATUS.md`.
