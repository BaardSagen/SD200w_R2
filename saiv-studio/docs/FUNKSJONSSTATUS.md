# Funksjonsstatus – 8. september 2026

| Område | Implementert og kontrollgrunnlag | Gjenstår / avgrensning |
|---|---|---|
| Windows-program | Versjon 0.2.0: direkte terminaloppstart, lys kompakt verktøylinje, fem sider, direkte ASCII-/kontrolltegn; oppstart/fokus/navigasjon/lukking GUI-testet | Full DPI-/skjerm-/PC-matrise |
| Kommunikasjon | COM-liste, manuell port/baud/paritet, asynkron RX/TX, terminal, opptak, eksplisitt reconnect | Fysisk gjennomgang av alle instrumenttilstander |
| Detect | 9600, 8N1 og programvareemulert 7E1; gjenkjenner loggerbanner, menyer og måling | Andre baudrater velges manuelt; ikke alle firmwarevarianter bekreftet |
| Menu | 250 ms ro, S fra oppstart, M fra status, ingen ny vekking i hovedmeny, begrenset tidsavbrudd | Fysisk akseptanse; ukjent meny krever inspeksjon |
| Download | F, fragmentert Refresh disk Y/N, ett Y, bekreftelse/feil/timeout, bevart delvis mottak | Reelle lange nedlastinger og alle loggervarianter |
| Import/eksport | CTD N-rader, FIELDS-filer, navngitte tabeller, CSV; tre virkelige eksempelfiler testet | Ingen proprietære binærformater eller multiline-CSV-felt |
| Grafer | Kanalvalg, profil med dybde nedover, kanaloversikt, kryss/tooltip, statistikk | Ikke full gammel grafverktøykasse; ingen zoom/panorering eller trykklar grafeksport |
| Utilities | Radsplitt, verdiutvalg, medianbasert spike-kolonne, gain/offset, lineær standardnivå-interpolasjon | Blandede opp/ned-profiler må splittes; ingen ekstrapolasjon |
| Beregninger | Offisiell GSW: SP, SA, CT, tetthet, sigma0, lydhastighet, dybde, O2-løselighet; testet kjente referanser og ugyldige verdier | Krever korrekte enheter/sted/temperaturskala; O2 antar standard atmosfære; ikke identisk med gamle formler |
| Loggerfiler | Mappesøk, utvalg, kopiering, størrelseskontroll og nytt navn ved eksisterende målfil | Ingen disk-refresh uten eksplisitt Download; ikke innholds-hash ved kopiering |
| Instrumentkalibrering / firmware | Ikke implementert | Protokoll- og akseptansearbeid nødvendig |
| GPS, SMTP, spesialiserte sonarformater | Ikke implementert | Egne arbeidsområder |

Importer begrenses til 64 MiB, én million rader, 128 kolonner og 12 åpne datasett. Mottaksbuffer er begrenset; overflyt stopper forbindelsen med feilmelding. Ugyldige verdier beholdes som manglende, aldri som forrige gyldige verdi. C (ledningsevne) og c (lydhastighet) holdes atskilt. Beregning/filtrering lager avledede datasett og overskriver ikke kilden automatisk.

Testresultatene ligger i `test-results`, kjernetestene i `tests/core_tests.cpp`. Historisk Delphi-kode er ikke inkludert i eller nødvendig for programmet. Originalprosjektets dokumentasjon og EXE-er beholdes separat.

0.2.0 erstatter 0.1.0-grensesnittet etter brukerens tilbakemelding. Tastaturtesten bruker filtransport, ikke et instrument. Siste rapport: `test-results/terminal_input_validation.json`. Fysisk instrumentakseptanse gjenstår.
