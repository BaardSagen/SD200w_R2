# SIT 1.4.13 – firmware for PCB 3.1.2 og 3.3.0

28. oktober 2026. Program: **SAIV_Instrument_Terminal_v1.4.13_Oct2026.exe**.
Kunden trenger fortsatt bare én EXE. Utgaven er usignert.

Help > Firmware støtter nå OSU107 og SAIV110 med OSU-M-maskinvare **3.1.2**
og **3.3.0**. SIT leser enhetens identitet og kontrollerer maskinvaren mot
USB-konfigurasjonen og en ny avlesning fra enheten. Riktig serverkanal velges
automatisk. Det finnes ikke noe manuelt valg som kan overstyre maskinvaren.

- 3.1.2 bruker `firmware/osu107_saiv110/hw_3-1-2/`.
- 3.3.0 bruker `firmware/osu107_saiv110/hw_3-3-0/`.

Versjonsoversiktens maskinvare, BIN-filnavn og README-adresse må tilhøre samme
kanal. Ukjente revisjoner og kryssede varianter avvises. Identitet kontrolleres
igjen før oppdateringen starter. Eksisterende SHA-256, full tilbakeavlesning,
konfigurasjonsbackup og verifikasjon etter omstart er beholdt.

Flerfilkonverteringen fra 1.4.12 er uendret. Nytt versjonsnummer gjør at også
brukere av 1.4.12 kan få utvidelsen gjennom Help > Update software.
Serverpakke og opplastingsrekkefølge: `update_server/LAST_OPP_1.4.13.md`.

## Intern bygg- og testinformasjon

Bygg: `analysis/build_single_exe_1413.py`, intern modul `SIT_Import153.dll`.
Bevart 1.4.12-runtime er grunnlag. Native runtime endres bare ved DLL-referanser,
About/versjon og PE-kontrollsum; den eksisterende Convert-dispatcheren beholdes.
1.4.12-kilden er bevart i `analysis/reference/sit_import_v1412`, og historisk
bygg og statisk kontroll peker nå på arkivet. Tidligere EXE-er og pakker beholdes.

Protokolltester inkluderer begge produkter på begge maskinvarerevisjoner,
kryssede serverkanaler, feil filnavn, ukjent maskinvare, endret identitet og
eksisterende feilforløp. Begge serverkanalene er kontrollert med produksjonens
WinINet-kode, manifestparser, SHA-256 og filtrering av kundevendte versjonsnotater.
Kundevendt filtrering dekker også interne instruksjoner i dagens servernotater.

GUI-testen bruker en egen runtime-kopi på privat skrivebord med fysisk
serieportåpning deaktivert og registeret erstattet av minnestubber.
Firmwarevinduets tekst, minste størrelse, manglende tilkobling, sperret
oppdatering og programversjon kontrolleres, sammen med flerfilkonverteringen.
Statisk kontroll knytter de innebygde modulene til levert EXE.

Samlerapport: `analysis/firmware1413_release_validation.json`.
Ingen fysisk firmwareoppdatering, serverpublisering, signering, commit eller push.
