# SAIV Instrument Studio 0.3.1

0.3.1 retter en oppstartsfeil som presset terminalen sammen når ingen målefil var åpen. Vanlig oppstart uten demo er kontrollert i tre vindusstørrelser. Regresjonstest: `analysis/test_studio_startup031.py`.

Et selvstendig Windows-program med moderne terminal, direkte tegntasting og enkle instrumentknapper. Starter rett i terminalen. Ingen installasjon, server eller konto kreves.

## Bruk

1. Kjør `SAIVStudio.exe`, trykk **Autodetect**, velg instrumentet og koble til.
2. Skriv direkte i terminalen. Enter sender CR; Backspace og kontrolltegn beholdes. **Setup** åpner manuelle portvalg.
3. **Download** mottar SD200-data. For USB-loggere brukes disk-refresh; åpne deretter **Instrument > Logger files** for å kopiere filene.
4. **Convert** åpner målefilen med SITs valg for felt, enheter, originalkolonner, Fahrenheit, salinitet, dybde, PAR og oksygen. **Merge** kobler filer etter tidsstempel.
5. **File > Open measurements** åpner CSV, loggertekst og eksisterende SD2. Under Measurements finnes tabell, tidsgrafer, profiler og Multigraph. Musehjulet zoomer; dobbeltklikk nullstiller grafen.
6. **Save** i målevisningen lagrer CSV med kolonnenavn, alle rader og måleopplysninger. **Save** i terminalen lagrer terminaltekst. **Export > FIELDS** tilbyr SIT-kompatibel loggertekst.

Nye data trenger ikke SD2. Gamle SD2-filer må fortsatt ligge sammen med tilhørende RF2 og eventuelle OX2/OP2/SF2. SF2 kontrolleres mot SD2 før åpning. CSV er én tekstfil med semikolon som skilletegn og måleopplysninger på kommentarlinjer som begynner med `#`.

**Interval** og **TIME/DATE** aktiveres etter valgt Autodetect-resultat. Dialogene kontrollerer instrumentets svar. Surface-intervall bruker valgt `config/system.ini`; originalfilen sikkerhetskopieres før endring. Instrumentet etterlates stoppet.

Data-menyen inneholder radutvalg, filtrering, spike-fjerning, justering og standarddybder. Disse lager et nytt datasett. Print skriver terminaltekst eller måletabell; grafutskrift er ikke implementert.

## Status

Utviklingsutgave for **Windows x64 / DirectX 11**. Mac- og Linux-utgaver følger ikke med. Grensesnittet er laget etter gjennomgang av kjørende SIT 1.4.3, med brukerens ønske om enkel betjening og nytt utseende.

Kjerne-, fil-/formel- og innstillingsprotokolltester følger med. Fysisk instrumentakseptanse av **Studio 0.3.1** gjenstår. Tidligere fysiske SIT-tester er ikke en fysisk test av Studio. Full SIT-paritet, kalibrering, firmwareoppdatering, alle gamle spesialeksporter og trykklar grafeksport er ikke ferdige.

Se [funksjonsstatus](docs/FUNKSJONSSTATUS.md), [kommunikasjon](docs/KOMMUNIKASJON.md) og [kildegrunnlag](docs/KILDEGRUNNLAG.md).

## Bygg

Installer Visual Studio med Desktop development with C++, Windows SDK, CMake og Ninja. Kjør `build.cmd`. Skriptet bygger x64 Release med statisk C++ runtime og kjører CTest. Programmet blir `build/SAIVStudio.exe`. Vendorkilde er inkludert; ingen nedlasting trengs.

`--demo` viser syntetiske data. `--open <fil>` åpner en målefil. `--terminal-test <fil>` erstatter terminalens instrumenttransport med en testfil. GUI-testen i det komplette prosjektet er `analysis/test_studio_gui030.py`; den krever Python/Pillow og bruker et eget programvindu.

Portvalg lagres i `%LOCALAPPDATA%/SAIV/InstrumentStudio/settings.txt`. Konverteringsvalg lagres separat fra SIT under `HKCU/Software/SAIV/InstrumentStudio/ConvertPresetsV1`.

Tidligere 0.2.0-kilder er bevart i `analysis/reference/saiv_studio_v020`. Original SIT og tidligere leveranser er beholdt. Se [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
