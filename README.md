# SAIV Instrument Terminal

Windows-program for kommunikasjon med SAIV-instrumenter og loggere.

## Siste leveranse: 1.4.10

**[Last ned SAIV Instrument Terminal 1.4.10](https://github.com/BaardSagen/SD200w_R2/raw/refs/heads/main/SAIV_Instrument_Terminal_v1.4.10_Sept2026.exe)**

Programmet leveres som ?n EXE med innebygde komponenter. Convert tilbyr valg av beregningsmetoder og enheter. Help > Quick guide har 26 emner med betjening, forklaringer og eksempler; salinitetsemnet forklarer SD208s PSS-78-beregning og betegnelsen S.

Les [salinitetsguiden for 1.4.10](LES_MEG_Salinity_Guide_1410.md) og [metodevalgene i Convert](LES_MEG_Conversion_Models_147.md).

Serverpakken ligger i [update_server](update_server). F?lg [opplastingsrekkef?lgen](update_server/LAST_OPP_1.4.10.md), med latest.json sist. GitHub-push laster ikke opp pakken til saiv.no.

SHA-256 for EXE: `d7e765a163ee20da144a2b61ebf7376218a125e318a30f4982b646ff8d4bd731`.

Tidligere leveranser er bevart som historikk og bygggrunnlag. Se [prosjektstatus](sd200DOc/PROSJEKTSTATUS.md) for tester og begrensninger.

## Funksjoner

- Åpner Instrument-vinduet ved oppstart.
- Detect søker på flere COM-porter og gjenkjenner blant annet SD200, OSU107 og SAIV110.
- Velg instrument med klikk og OK, eller dobbeltklikk.
- Download håndterer disk-refresh for støttede loggere og viser beskjed dersom logging må stoppes først.
- Større terminalhistorikk og blått grensesnitt.
- CTS/DSR-flytkontroll deaktivert.

## Skjermbilder

Instrument-vinduet med terminal, måledata og snarveier:

![Instrument-vindu med måledata](sd200DOc/images/instrument.png)

Detect med to instrumenter funnet:

![Detect med SD200 og SAIV110](sd200DOc/images/detect.png)

Klikk på ønsket rad og velg OK, eller dobbeltklikk raden. Bildene er fra tidligere tester av samme grensesnitt. Portnumre og signalstatus er eksempler fra testoppsettet.

## Videre arbeid på en annen PC

Start med **[OPPSTART_NY_PC.md](OPPSTART_NY_PC.md)** for oppsett, kontroll av filene og kjøring av tester.

- [Prosjektstatus og åpne punkter](sd200DOc/PROSJEKTSTATUS.md)
- [Formelkartlegging](sd200DOc/FORMELKARTLEGGING.md) og [formelkontroll](sd200DOc/FORMELKONTROLL.md)
- Alle `LES_MEG_*.md` i rotmappen beskriver tidligere endringer og leveranser.
- `analysis/`: byggskript, assembler, rekonstruerte formler, tester, manifester og analyseresultater.
- `analysis/runtime_test/`: historiske GUI-testresultater, skjermbilder og to forsøksprogrammer.
- `osu107Doc/`: loggerprotokoll, integrasjonsnotater og konverteringseksempler.
- `docs/`: historisk instrument-/firmwaredokumentasjon og referansemanualer.

Original og tidligere EXE-utgaver er bevart som inngangsfiler for hashbundne bygg og tester. **Siste lokale leveranse er SD200W_SAIV_v1.0.3_Sept2026.exe; publisert utgave er foreløpig 1.0.1.** Forsøksprogrammer i `analysis/runtime_test/` er ikke leveranser.

Original Delphi-kildekode finnes ikke i prosjektet. Videreutviklingen bygger på analyse og patching av Windows-programmet. Formelproblemer er dokumentert, men ikke rettet i EXE.

## ImGui 0.2.0 – enkel terminal

[Portabel utgave](saiv-studio/releases/SAIVStudio_0.2.0_Windows_x64.zip) og [komplett kilde](saiv-studio/releases/SAIVStudio_0.2.0_Source.zip). Åpner direkte i terminal med Autodetect/Download og direkte tegntasting. Se [README](saiv-studio/README.md). Erstatter 0.1.0-grensesnittet etter brukerens tilbakemelding.
