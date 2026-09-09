from pathlib import Path
r=Path(__file__).resolve().parents[1]
docs={
'README.md':'''# SAIV Instrument Studio 0.3.0

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

Kjerne-, fil-/formel- og innstillingsprotokolltester følger med. Fysisk instrumentakseptanse av **Studio 0.3.0** gjenstår. Tidligere fysiske SIT-tester er ikke en fysisk test av Studio. Full SIT-paritet, kalibrering, firmwareoppdatering, alle gamle spesialeksporter og trykklar grafeksport er ikke ferdige.

Se [funksjonsstatus](docs/FUNKSJONSSTATUS.md), [kommunikasjon](docs/KOMMUNIKASJON.md) og [kildegrunnlag](docs/KILDEGRUNNLAG.md).

## Bygg

Installer Visual Studio med Desktop development with C++, Windows SDK, CMake og Ninja. Kjør `build.cmd`. Skriptet bygger x64 Release med statisk C++ runtime og kjører CTest. Programmet blir `build/SAIVStudio.exe`. Vendorkilde er inkludert; ingen nedlasting trengs.

`--demo` viser syntetiske data. `--open <fil>` åpner en målefil. `--terminal-test <fil>` erstatter terminalens instrumenttransport med en testfil. GUI-testen i det komplette prosjektet er `analysis/test_studio_gui030.py`; den krever Python/Pillow og bruker et eget programvindu.

Portvalg lagres i `%LOCALAPPDATA%/SAIV/InstrumentStudio/settings.txt`. Konverteringsvalg lagres separat fra SIT under `HKCU/Software/SAIV/InstrumentStudio/ConvertPresetsV1`.

Tidligere 0.2.0-kilder er bevart i `analysis/reference/saiv_studio_v020`. Original SIT og tidligere leveranser er beholdt. Se [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
''',
'docs/FUNKSJONSSTATUS.md':'''# Funksjonsstatus – Studio 0.3.0, 10. september 2026

| Område | Implementert | Avgrensning |
|---|---|---|
| Grensesnitt | Direkte terminaloppstart, moderne lys ramme/mørk terminal, vanlige instrumentknapper, menyer og dialoger | Windows x64; ingen Mac/Linux-leveranse |
| Terminal | Direkte ASCII/kontrolltegn, fokusbeskyttelse, tekstlagring, RX-opptak, portvalg og reconnect | Ingen full ANSI-terminalemulering |
| Autodetect | 9600 med faktisk 8N1/7E1, meny-/bannerkontroll, akseptert resultat videreføres | Alle adaptere/firmwarevarianter er ikke fysisk testet |
| Download | Menybevisst SD200-nedlasting og logger-refresh med ett Y og kontroll av svaret | Lange fysiske nedlastinger gjenstår; USB-filer kopieres fra Logger files |
| Interval/TIME-DATE | Elleve intervaller; SD200/OSU107/SAIV110; PC-LT/UTC; tilbakeavlesning; én SD200-klokkeskriving; Surface config-backup/flush/U | Protokolltestet; Studio-transporten er ikke fysisk verifisert |
| Åpning | SD2/RF2/OX2/OP2, SF2 med fingerprint, FIELDS/full loggertekst, gamle N-rader og CSV | SD2-leseren støtter undersøkt 52-byte format. Følgefiler må følge med |
| Lagring | CSV som standard med alle kolonner/rader/måleopplysninger; FIELDS-eksport og terminaltekst | SD2 tilbys ikke som nytt arbeidsformat. Intern kompatibilitetsskriver er beholdt som testgrunnlag |
| Convert | SITs felt-/enhetsvalg, C→S, Fahrenheit, fixed-position real depth, PAR-arealenhet, OX/OxR, originalkolonner og egne presets | Manglende nødvendige inngangsverdier må avklares |
| Formler | Dokumenterte SIT PSS-78/lydhastighet/EOS-80/gravity/oksygenrutiner, testet mot registrerte EXE-referanser | Ingen påstand om bitidentitet med x87 ved alle inngangsverdier |
| Merge | Mappeskanning, én/to tilleggsfiler, 0–10 s toleranse, nærmeste tidspunkt, dato/tid og alle felt | Samme krav til eksplisitte radtider som SIT |
| Grafer | Parvise tidsgrafer/profiler, faktisk tid når dato/tid finnes, T-S, opptil ti kanaler, zoom og kryssavlesning | Multigraph viser separate paneler. Panorering, alle gamle grafvalg og grafutskrift mangler |
| Dataverktøy | Radutvalg, verdifilter, medianbasert spike-fjerning, gain/offset og lineær standardnivå-interpolasjon til nytt datasett | Standardnivåer krever én monoton profil; ingen ekstrapolasjon |
| Loggerfiler | Mappeskanning, utvalg og kopiering med størrelseskontroll og nytt navn ved kollisjon | Kopier kontrolleres med størrelse, ikke innholdshash |
| Print | Terminaltekst eller måletabell med sideinndeling | Fysisk skriver ikke testet; grafer skrives ikke ut |
| Andre SIT-funksjoner | Ikke fullført | Kalibrering, firmware-/programoppdatering, GPS-instrumentintegrasjon, SMTP og spesialeksporter |

CSV beholder kolonnerekkefølge, siterte felt og brøkdelssekunder. C og c holdes atskilt. CSV begrenses til 64 MiB, 200 000 rader og 128 kolonner; SIT/FIELDS-parseren til 20 MiB, 200 000 rader og 100 kolonner. Tolv datasett kan være åpne samtidig.

Tester: `tests/core_tests.cpp`, `tests/compat_tests.cpp`, `tests/settings_tests.cpp`. Filtestene bruker ekte 79-/3-/43-raders tekstfiler og en gammel 7-raders SD2-fil, og kontrollerer CSV-rundtur, SF2, manglende verdier, formler og konvertering. GUI-kontroller og skjermbilder ligger i `test-results/v030`.
''',
'docs/KOMMUNIKASJON.md':'''# Kommunikasjon – Studio 0.3.0

7E1 settes faktisk i UART: syv databiter, even-paritet og én stoppbit. `GetCommState` leser innstillingen tilbake. Adaptere som avviser dette gir feil; ingen overgang til softwareparitet foretas. Tidligere softwareparitetskode er fjernet.

Autodetect prøver 9600/8N1 og 9600/7E1, lytter og gjenkjenner komplette instrumentmenyer eller loggeridentitet. Valgt port og innstillinger brukes ved tilkobling. Andre baudrater velges i Setup. Søk sender ikke start-, slette- eller kalibreringskommandoer.

Terminal-/downloadprotokollen venter minst 250 ms etter mottatt tekst. S brukes fra oppstartsmeny, M fra status. G undersøker en stille port; avgrenset I-vekking brukes bare uten mottatt tekst, med minst 50 ms mellom I. Delvis/ukjent meny tillater ikke blind videre vekking. Avslutt et automatisk forløp med Cancel før manuell terminaltasting.

Download sender F. Et komplett Refresh disk Y/N besvares med ett Y. Feil, manglende bekreftelse og timeout vises. SD200-data og terminaltekst beholdes. Loggerfiler kopieres fra USB-disken under Instrument > Logger files.

Interval og TIME/DATE krever valgt Autodetect-resultat og aktiv forbindelse. Protokollkoden fra SIT bruker komplett respons, mottaksro og tilbakeavlesning. Klokkeekko håndteres tegnvis med egne ventetider. Innstillingsjobben kjører i bakgrunnen med eksklusiv bruk av serialtransporten; terminalkommandoer sperres under jobben. Loggerstatus kan kreve kontrollert gjenåpning av porten, med ny kontroll av identitet og serienummer.

SD200-intervallet settes fra den annonserte menyen og leses tilbake. SD200-klokken skrives én gang med tidskompensasjon. OSU107 setter SD200- og loggerklokken separat. Surface stoppes før klokke/intervall; intervallet endres i valgt USB `config/system.ini`, med sikkerhetskopi, flush, venting og bekreftet U/APPLY.

GUI-testen bruker filtransport og sender ikke til fysisk instrument. Fysisk akseptanse av Studio 0.3.0 gjenstår. Tidligere fysiske SIT-resultater gjelder den utgaven og kan ikke automatisk overføres til Studio.
''',
'docs/KILDEGRUNNLAG.md':'''# Kildegrunnlag

Studio er et eget C++-program og laster ikke Delphi-EXE-en. Grensesnittet er laget etter brukerens bestilling og gjennomgang av kjørende SIT 1.4.3; se prosjektets `sd200DOc/SIT_GUI_GJENNOMGANG.md`.

`src/sit/` inneholder egne kopier av prosjektets SIT-moduler for loggerfiler, konverteringsvalg, presets, Merge, native filformat og innstillingsprotokoll. Originalene under `sit_import/` er beholdt. Dialogene bruker Studio-navn, moderne Windows-kontroller/Segoe UI og egen preset-registersti.

`sit_compat.cpp` implementerer dokumenterte SIT-beregninger i C++ med registrerte maskinkoderesultater som testreferanser. Merk callback-rekkefølgen: `sitFormula(0,C,T,P)`, mens SITs konverteringsmodul bruker `sitConversionFormula(0,P,C,T)`. Real depth bruker SITs fixed-position uttrykk med EOS-80-tetthet og gravity, ikke en alternativ trykkpolynom- eller TEOS-10-gren.

ImGui og GSW er versjonsfestet i THIRD_PARTY_NOTICES.md. GSW og eldre kjernetester er beholdt, men standardkonverteringen i 0.3.0 bruker SIT-rutinene. Brukerens instrumentikon er beholdt.

Bygg med `build.cmd`. Historiske engangsskript i `analysis` er ikke den generelle byggprosessen. 0.2.0 er arkivert i `analysis/reference/saiv_studio_v020`. Bevar ekte UART 7E1, komplette menyer, mottaksro, skillet C/c og tapfri CSV-rundtur.

Windows-vinduer, fildialoger og serieporttilgang må tilpasses eller erstattes ved senere Linux-/Mac-portering. Beregnings-, fil- og protokollkjernen er skilt fra grensesnittet; denne leveransen har bare Windows-EXE.
'''
}
for path,text in docs.items():(r/'saiv-studio'/path).write_text(text,encoding='utf-8')
