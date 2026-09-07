# Prosjektoverlevering — MiniSoft SD200W / SAIV

Oppdatert: 7. september 2026. Arbeidsmappe: `C:\cprojects\delphi`.

## Start her neste gang

1. Les dette notatet og brukerens nye oppgave.
2. Bruk **SD200W_SAIV_v1.0.1_Sept2026.exe** som utgangspunkt for nye endringer.
3. Les relevante dokumenter og byggskript i `analysis` før patching. Mange skript krever en bestemt eldre kildefil og SHA-256; de kan ikke ukritisk kjøres på siste utgave.
4. Lag en ny programkopi og behold tidligere leveranser. Verifiser relevante endringer og lever den konkrete EXE-filen.

Vi har ikke original Delphi-kildekode. Arbeidet består av analyse og patching av en 32-bits Delphi Windows-EXE: maskinkode, PE-ressurser og DFM-skjemaer. Dokumentasjonen om instrumentfirmware er en separat kilde og må ikke forveksles med Windows-koden.

## Siste leveranse

Fil: [SD200W_SAIV_v1.0.1_Sept2026.exe](../SD200W_SAIV_v1.0.1_Sept2026.exe).

- About: `Version: 1.0.1 Sept.2026`.
- Windows FileVersion og ProductVersion: `1.0.1 Sept.2026`.
- Numerisk Windows-versjon: `1.0.1.0`.
- SHA-256: `ebd75cdb4b93ff2e703b518550dfd2bce51490d8f12b6f0cb6f311f0a5f92068`.
- Bygg: `analysis/build_version_1_0_1.py`.
- Manifest: `analysis/version_1_0_1_manifest.json`.
- Kilde for denne leveransen: `SD200W_SAIV_OSU107_NoHandshake.exe`.
- Sist endret bare About-ressursen og versjonsmetadata med nødvendige PE-headerendringer. Ingen instruksjonskode endret i versjonsoppdateringen.
- Windows VersionInfo og PE-sjekksum kontrollert. GUI startet i Instrument-vinduet uten feildialoger.

**Ikke bruk eldre `SelectInstrument`, `final` eller `Instrument` som om de var nyeste fil.** Brukeren viste tidligere skjermbilde av SelectInstrument som fortsatt hadde gammelt copyright-felt. Nyeste versjon har SAIV A/S i dette feltet.

## Brukerens arbeidsmåte og preferanser

- Kommuniser på norsk, enkelt og konkret.
- Brukeren vil ha faktiske endringer og testbare EXE-kopier.
- Tekster i programmets nye feilmeldinger skal være på engelsk. Tidligere norske tekster fikk tegnkodingsproblemer.
- Behold tidligere filer; ingen opprydding/sletting er avtalt.
- Ikke endre formler eller kalibrering bare fordi en analyse har funnet et problem. Den siste formeloppgaven var dokumentasjon og kontroll, ikke retting.
- Hardware på portene og instrumenttilstand kan ha endret seg siden sist. Kontroller dette før nye tester.

## Implementerte funksjoner

### Instrument-vindu og utseende

- Programmet åpner Instrument/terminal automatisk etter at initialisering er ferdig.
- Den første direkte oppstartspatchen krasjet med access violation rundt `0059B007`, read `00000A61`. Den senere utsatte oppstarten fungerer. Ikke gjeninnfør direkte åpning under tidlig initialisering.
- Større terminalhistorikk: tidligere dokumentert økning til 2000/18000 linjer for de to grensene.
- Blå paneler `#508CC6`, lys terminalbakgrunn, opprinnelig svart Fixedsys-terminaltekst.
- Rammer rundt paneler og ikoner; svart skillelinje ved terminalens rullefelt.
- Call og Receive er skjult/frakoblet.
- Detect ligger øverst på plassen til gamle Setup. Setup ligger under Print på plassen til gamle Detect.
- Developer: SAIV AS. Disclaimer: SAIV A/S.

### Detect

- Søk på flere porter parallelt.
- Baud/paritet prioriteres 9600 None, 9600 Even, 4800 None, 4800 Even før øvrige eldre alternativer.
- OSU107 og SAIV110 gjenkjennes fra banner ved åpning av porten. For disse USB-enhetene er baud/paritet ikke tilsvarende fysisk UART-krav.
- Passiv lytting etter portåpning før vanlige søkekommandoer. Det finnes forsinkelse mellom lukking/åpning for at USB/DTR-hendelsen skal registreres.
- Lysegrønn markering gjelder bare funnet instrumentrad; tidligere feil med full grønn flate og rader som forsvant er behandlet.
- Klikk på rad velger «Use as Instr». De tre gamle valgene Instrument/Aux/None er skjult. OK bekrefter, dobbeltklikk gjør det samme. Valg skal ikke tas i bruk før bekreftelse.

### Download og disk-refresh for loggerne

- Gjenkjenner `Refresh disk Y/N` i en aktiv Download-sekvens.
- Avslutter gammel nedlastingsflyt og sender **én Y uten CR/LF** gjennom eksisterende serierutine.
- Leser instrumentsvaret etter Y, med Windows-meldingsbehandling aktiv i ventetiden (omtrent 5 sekunder).
- Svar som starter med `System disk refresh will start in 3 seconds.` gir meldingen `Preforming refresh off disks` som lukker seg etter 3 sekunder. Den engelske stavemåten er beholdt fra brukerens ønske.
- Svar som starter med `ERR: stop surface-logger and wait for the current sample to finish` gir:
  `Stop logging and wait for the current sample to finish before refreshing the disk. Then click Download again.`
- Ukjent/manglende svar gir: `Disk refresh was not confirmed. Check the terminal response.`
- Et gjentatt Y/N i feilsvaret skal ikke sende enda en Y.
- Programmet stopper ikke logging automatisk og gjenåpner ikke automatisk porten etter USB-refresh.
- Loggernes refresh-prosa filtreres ut av den gamle måleparseren slik at teksten ikke utløser «Error in ref line».
- Eksisterende Log og vanlig instrumentnedlasting må bevares.

### CTS/DSR og COM-port

- Alle fire SetCommState-kall går nå gjennom wrapper som nuller `fOutxCtsFlow`, `fOutxDsrFlow`, `fDsrSensitivity`.
- Masken er `DCB.Flags &= 0xFFFFFFB3`.
- DTR/RTS og øvrige innstillinger beholdes. De må ikke deaktiveres vilkårlig: USB-loggernes oppstartsbanner bruker portåpnings-/DTR-hendelser.
- CTS/DSR kan fortsatt vise «on» i søkeresultatet fordi det er fysisk signalstatus, ikke flytkontrollinnstilling.
- COM7 svarte i en fysisk vekketest ved 9600 8N1 uten CTS/DSR-flytkontroll.
- Brukeren bekreftet at NoHandshake-utgaven fungerte.

## Åpne punkter i kommunikasjon

### Treg OK i Setup

Brukeren rapporterte treghet. Ikke gjenskapt med uendrede innstillinger: dialogen lukket etter omtrent 15 ms i eldre utgave og 31 ms i NoHandshake. Dette måler bare dialoglukking, ikke fullført portbytte/etterbehandling. Det er **ikke levert en dokumentert separat rettelse for denne forsinkelsen**.

### SD200 vekking etter H/Download/Cancel

Brukeren opplevde at porten virket låst. Tidligere tester kunne ikke gjenskape problemet når passiv tilstand var bekreftet. Ikke erklær dette som endelig løst.

- `I` har ulik betydning avhengig av meny/tilstand: gjentatt I etter at menyen er nådd kan åpne intervallinnstilling.
- `H` i meny/remote kan sette instrumentet passivt. H i løpende målestrøm ble ignorert i tidligere test.
- Ikke fortsett å sende vekke-I etter gjenkjent meny.
- Tidligere fysisk test brukte COM7 for SD200, COM11 for SAIV110. Dette er historiske portnumre, ikke en garanti om dagens oppkobling.
- Noen tidligere prøveskript gikk utilsiktet inn i intervallmeny. Les skriptene før gjenbruk; ingen kalibreringsendring var tilsiktet.
- Sist dokumenterte vekketest lot instrumentet være vekket; menyen varsler mulig automatisk målestart etter 10 sekunder. Ikke anta at instrumentet fremdeles er passivt.

## Formelarbeidet

Les:

- [FORMELKARTLEGGING.md](FORMELKARTLEGGING.md): formler, bruksområder, kodeadresser, sikkerhetsnivå i identifikasjon og komplett Python-vedlegg for kjerneformlene.
- [FORMELKONTROLL.md](FORMELKONTROLL.md): svakheter, referansetester og hva som fortsatt ikke er bekreftet.

Analysert formelfil var NoHandshake. Siste 1.0.1-utgave endrer bare versjonsressurser, så formelkoden er bevart.

### Funn

1. **Oksygen:** wrapper `0x0050BC10` tvinger S=34,5 når filens S/C-kanalflagg er null. Numerisk test ved 20 °C, 760 mmHg og 100 % metning: ferskvann 9,0924 mg/l, tvunget 34,5 gir 7,4179 mg/l (18,42 % lavere). Kodeatferden er bekreftet. Det er ikke bekreftet at brukerens aktuelle filer/visninger går gjennom denne grenen.
2. **Ugyldige inndata:** saltholdighetsrutinen returnerer 0 for C<0,01, også negative verdier. Videre beregning kan da produsere tilsynelatende gyldig lydhastighet. Det gjenstår å kontrollere hvilke ugyldighetsmarkører innleseren slipper igjennom.
3. **Lav salinitet:** ordinær PSS-78 uten funnet Hill-korreksjon i undersøkt rutine. Sprang ved C=0,01 mS/cm. Vurder ferskvann/brakkvann særskilt.
4. **Temperaturskala:** seks GSW-referanser stemmer når T68=T90×1,00024. Ikke avklart om instrument-/filtemperaturen allerede har riktig skala; ikke legg inn dobbel korreksjon.

**Ingen av disse formelforholdene er rettet i EXE.**

### Verifisering

- 24 sammenligninger av rekonstruert Python og binær maskinkode bestod for lydhastighet, saltholdighet og tre tetthetsgrener.
- Seks eksterne saltholdighetsreferanser bestod med korrekt temperaturskala.
- Tre rundturer S→C→S bestod.
- Tre oksygenprøver stemte mellom rekonstruksjon og maskinkode.
- Samsvar mellom rekonstruksjon og EXE beviser ikke alene faglig riktighet i opprinnelig kode.
- Alle disse prøvene var emulatorbaserte, uten instrumentkommandoer.
- En innledende feil i argumentrekkefølgen i invers-testen ble korrigert. Det var en testfeil, ikke en programfeil.

Kilde/testfiler: `analysis/recovered_formulas.py`, `analysis/test_recovered_formulas.py`, `analysis/audit_formulas.py`, `analysis/formula_numeric_validation.json`, `analysis/formula_audit_tests.json`.

## Navn og signering

- Nyeste leveranse har SAIV AS / SAIV A/S i relevante About-/versjonsfelter.
- I Clean-steget ble rester av gammelt sertifikat fjernet, copyright og innebygde e-posttekster endret. Søk i NoHandshake etter gamle navneord i ASCII, UTF-16LE og UTF-16BE ga ingen treff.
- Dette er ikke en garanti for at programmets historiske opprinnelse er umulig å identifisere fra maskinkode. Eldre programkopier og historiske analyseskript inneholder fortsatt gamle navn.
- Signering/SmartScreen er **utsatt av brukeren**. Ikke opprett betalte tjenester eller publiser programmet som del av rutinearbeid.
- Originalen hadde et innebygd sertifikat, men Windows stolte ikke på sertifikatkjeden i tidligere sjekk. Nyeste endrede program er usignert.
- Hosting på egen HTTPS-server fjerner ikke i seg selv SmartScreen-varsel. Ingen serverpublisering eller signeringstjeneste er satt opp.

## Viktige byggfiler og rekkefølge

Seneste kjede:

```text
Refresh → Clean → RefreshReply → RefreshReply_EN → NoHandshake → v1.0.1 Sept.2026
```

| Område | Filer |
|---|---|
| Siste versjonsmetadata | `analysis/build_version_1_0_1.py` |
| CTS/DSR | `analysis/build_no_handshake.py`, `analysis/test_no_handshake.py` |
| Engelske refresh-tekster | `analysis/build_refresh_reply_en.py` |
| Refresh-svar | `analysis/build_refresh_reply.py`, `analysis/refresh_reply.s`, `analysis/test_refresh_reply.py` |
| Loggerprosa og navneopprydding | `analysis/build_logger_clean.py`, `analysis/logger_refresh_clean.s`, `analysis/test_logger_clean.py` |
| Klikk/dobbeltklikk i Detect | `analysis/build_select_instrument.py`, `analysis/select_instrument.s` |
| USB-loggerdeteksjon | `analysis/build_logger_detect.py`, `analysis/logger_detect.s` |
| Utsatt Instrument-oppstart | `analysis/build_deferred_start.py`, `analysis/start_instrument_deferred.s` |
| Utseende | `analysis/build_blue_look.py` og manifestene for hver utgave |
| Full gammel disassemblering | `analysis/original-disassembly.txt` — original, ikke alle nyere patcher |
| Ny målrettet disassemblering | `analysis/disasm_formulas.py` — hardkodet NoHandshake som kilde |

Før nye kodeendringer: les filens forventede hash, inngangsfil og manifest. Mange tidligere skript er historiske trinn, ikke en samlet byggpipeline.

## Teknisk oppslagsdel

PE image base: `0x00400000`. GUI-programmet er 32-bits; 64-bits testverktøy må lese WOW64-PEB korrekt. Bruk RVA ved flyttet innlasting.

- MainForm: global peker ved base+`0x1C8964`.
- Instrument-serieobjekt: MainForm+`0x510`; aux +`0x514`.
- Serieobjekt: openflag +`0x24`, handle +`0x2C`, baud +`0x30`, port +`0x34`, paritet +`0x4C`.
- Portåpning `0x0047E8F8`, lukking `0x0047F9C4` (allerede hooket, bevar), sending `0x0047FFC4`.
- Opprinnelig SetCommState-stub `0x00407B5C`.
- Fire SetCommState-kallsteder `0x0047E6B2`, `0x0047E87A`, `0x0047E8EE`, `0x0047F427` er omdirigert i NoHandshake.
- Setup-handler `0x005A109C`, OK-handler `0x00513C0C`; Setup+`0x45D` instrumentendret, +`0x45E` auxendret.
- Download-knapp MainForm+`0x374` er en native TButton: bruk BM_CLICK på HWND ved test.
- Detect gjenbruker gammel TSpeedButton MainForm+`0x4EC`: parent-koordinatklikk ved test.
- HWND for relevante Delphi-kontroller finnes ved +`0x14C` i tidligere analyser; verifiser klassetype.
- Download/receive-hook ved `0x0059B308`; completed-line-parserkall ved `0x005496AA`.
- Eksisterende meldingspumpe `0x00502078`; `0x00583510` er ikke ProcessMessages.
- About-versionens opprinnelige caption-setter ved RVA `0x1A47C9` er NOP-et for å bevare egen versjonstekst.

## Testmiljø og kjente begrensninger

Python-pakker for Unicorn/Capstone ligger i `analysis/python_packages`. Skriptene legger dette inn i sys.path. `pefile` er også tilgjengelig i brukt Python-miljø.

`analysis/check_startup_windows.py` starter og avslutter sin egen programinstans, normalt på privat Windows-desktop. `--look-only` er en kort oppstartssjekk. `--live-rows` bruker brukerens desktop. `--detect` utfører instrumentsøk. Les testsekvensen før kjøring.

Kjent svakhet i kopierte GUI-harness: `--live-rows` uten `--detect` kan likevel gå inn i detect-kontroll ved sekund 6 og avslutte med `detection_closed_early`. Dette er ikke i seg selv en programfeil. `check_setup_latency.py` har denne arven og måler dialoglukking, ikke nødvendigvis fullført portbehandling.

GUI-/hardwaretester har ofte krevd eskalert verktøytilgang. Avslutt bare testprosessen som eget skript startet, ikke brukerens åpne program. Kjør ikke gamle fysiske wake-skript blindt.

## Mulig neste arbeid — avhengig av brukerens nye oppgave

- Reprodusere oksygenproblemet med en konkret fil uten S/C og brukerens valgte saltholdighet.
- Kartlegge ugyldighetsmarkører fra instrument/fil til avledede verdier.
- Avklare temperaturskala før noen formelkorreksjon.
- Undersøke Setup-forsinkelse ved faktisk endring/bytte av port.
- Eventuelt fortsette gjennomgang av kalibreringsformler, Rinko og profilberegninger.

Ikke anta at noe av dette er bestilt implementert. Bevar siste fungerende program som referanse.

## GitHub og overføring til annen PC

Repository: https://github.com/BaardSagen/SD200w_R2

Første publisering 7. september 2026, commit `cb86897`, inneholdt bare siste EXE, README og to skjermbilder. Brukeren har deretter uttrykkelig bedt om alle LES_MEG-filer, formelkartlegging, prosjektstatus og resten av arbeidet slik at prosjektet kan videreføres på en annen PC. Dette erstatter den tidligere begrensningen av publiseringsinnholdet.

Den utvidede leveransen omfatter alle lokale prosjekt-/referansedokumenter, analyseskript, assemblerkilder, manifester, testresultater, skjermbilder og originale/historiske EXE-filer som byggene avhenger av. Se [OPPSTART_NY_PC.md](../OPPSTART_NY_PC.md) for installasjon, tester og begrensninger, og `analysis/transfer_inventory.json` for fillisten. Python-avhengigheter er versjonsfestet i `requirements-dev.txt`.

Siste leverte program er uendret. Formelproblemer er fortsatt bare dokumentert. Firmwarekildekode som omtales i separate referansedokumenter finnes ikke i denne arbeidsmappen og inngår ikke i overføringen.

Lokal gren `local-project` bevarer tidligere lokal historikk. Ingen tidligere leveranser eller grener er slettet. Bruk konkrete filvalg ved senere publisering; ikke `git add .`, `git clean` eller `push --all`.

Overføringen er kontrollert med rent Python-miljø i en separat eksport av Git-innholdet. Formel- og kommunikasjonstestene bestod, og siste versjonsbygg ga identisk EXE-hash. Se [OVERFORINGSKONTROLL.md](OVERFORINGSKONTROLL.md). Ingen fysisk instrumenttest ble utført.
