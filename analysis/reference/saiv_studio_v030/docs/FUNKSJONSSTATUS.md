# Funksjonsstatus – Studio 0.3.0, 10. september 2026

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
