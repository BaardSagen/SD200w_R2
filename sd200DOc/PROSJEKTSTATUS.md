# Prosjektoverlevering — SAIV Instrument Terminal (tidligere MiniSoft SD200W)

Oppdatert: 28. oktober 2026. Arbeidsmappe: `C:\cprojects\delphi\sd200w_r2`.

## Nyeste leveranse: 1.4.13 – TIME/DATE og Interval rettet

Brukeren bekreftet 28. oktober 2026 at 1.4.13 fungerer, og ba om commit og push.

Brukeren rapporterte at TIME/DATE og Interval åpnet Convert, og ba deretter
uttrykkelig om **1.4.13**. Dette erstatter forrige instruks om å beholde 1.4.12.
Nyeste EXE: `SAIV_Instrument_Terminal_v1.4.13_Oct2026.exe`.
Les `LES_MEG_Controls_1413.md`.

Årsak: batch-dispatcheren i 1.4.12 sendte alle felles klikk unntatt Merge til
Convert. De to innstillingsknappene bruker samme Delphi-handler med egne Tag-verdier.
Ny dispatcher beholder Convert for vanlig sender og sender merkede knapper
til den eksisterende kjeden for innstillinger/Merge. Klokke-, intervall-,
serie-, firmware- og beregningsprotokoller er uendret.

Eksisterende innstillingstester var ikke kjørt mot batch-endringen; det var
et hull i leveransekontrollen. Brukeren krevde at dette alltid gjøres fremover.
Fast regel i AGENTS.md krever nå samlet test av TIME/DATE, Interval, Convert
og Merge etter endringer i knapper, menyer eller felles handler, mot de faktiske
leveransemodulene. Gamle resultater alene er ikke godkjenningsgrunnlag.

Bestått: begge innstillingsdialoger for SD200, OSU107 og SAIV110, 11 intervallvalg,
LT/GMT-kontroll, avbrudd, sperring uten Detect og etter portbytte, Convert-knapp
og File-meny, enkeltfil/flerfil med identiske eksporter, Merge og firmware-/
software update-vindu. 12 maskinkodescenarier ved normal/flyttet base bevarer
registre og stakk. Testene kjører på privat skrivebord med simulert Detect,
registerstubber og fysisk serieportåpning sperret. Ingen faktisk klokke-,
intervall- eller firmwareendring på instrument. Samlet kontroll:
`analysis/validate_controls1413.py`, `analysis/firmware1413_release_validation.json`.

Bygg: `analysis/build_single_exe_1413.py`, runtime `analysis/single1413_settings`,
innebygd `SIT_Import155.dll`. EXE SHA-256:
`3c1f858d574b9498bdd6f422c674da0ff83226b2c0f3ed88a8980487941698c9`.
Serverpakke: `update_server/saiv_instrument_terminal_v1.4.13_oct2026.zip`,
`readme_v1.4.13.txt`, `latest.json`. Last opp latest.json sist. EXE-oppføringen
bruker små bokstaver som ZIP-adressen. ZIP SHA-256:
`ed7db6d8863dcff0053bd9faa5c1ced8b13f73ec4a60c2310e85ea0955ea4821`.
Pakkerapport: `analysis/update_server1413_validation.json`.
Fortsatt usignert. Ingen serveropplasting, commit eller push.

## Siste leveranse er 1.4.12 – endelig versjonsvalg, 28. oktober 2026

**Pakkefeil rettet samme dag:** Brukeren fikk «The ZIP does not contain the
expected program». Oppdatereren utleder et EXE-navn med små bokstaver fra
ZIP-URL-en, men tidligere ZIP hadde store bokstaver i EXE-oppføringen.
Pakkeskriptet bruker nå nøyaktig navnet fra URL-en, inkludert skrivemåte.
EXE-byte og versjon 1.4.12 er uendret. Ny ZIP SHA-256:
`f624a8c1e6e0db271bd3666f5246cbe07d74fa6f2927c518bf5a18ccb044fd2e`.
Last opp ZIP og latest.json på nytt, latest.json sist. Ingen serveropplasting
fra agenten. Eksisterende hjelpebinær reproduserte den gamle feilen og
godkjente korrigert ZIP, CRC, kandidatbyte og innebygd versjon frem til
installasjonsgrensen. Isolert inert testvert ble beholdt åpen; ingen faktisk
SIT-installasjon, omstart eller AppData-utpakking ble utført. Rapport i
`analysis/update_server1412_validation.json`. Brukeren ba uttrykkelig om at
regelen noteres til senere oppdateringer; den står nå øverst i AGENTS.md og
kontrolleres av `analysis/prepare_update_server_1412.py`.

Brukeren bestemte uttrykkelig at siste versjon skal være **1.4.12**, siden
ingen hadde lastet den opp. 1.4.13-utkastet er ikke leveransen.
Bruk `SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe` og de tre 1.4.12-filene i
`update_server`. Leveransen har både flerfilkonvertering og automatisk
maskinvarekontroll/firmwarevalg for 3.1.2 / 3.3.0. Kundens README er forkortet.

Bygg: `analysis/build_single_exe_1412.py`, arbeidsfiler i
`analysis/single1412_hw330`, innebygd `SIT_Import154.dll`.
EXE SHA-256: `3dbbed2e844a54057fd260c889514864ac050f24993780ed3d417f1a17bfcec1`.
Versjon 1.4.12.0 er kontrollert i launcher, runtime og software update-vindu.
Firmwarevindu med begge revisjoner, avvisning uten tilkobling og en ny
flerfilprøve med identiske eksporter bestod. Den komplette foregående
funksjonsakseptansen gjelder samme maskinvare-/konverteringsfunksjonalitet;
sluttendringen gjelder versjon, DLL-navn og user-agent. Ingen fysisk flashing.
Rapporter: `analysis/firmware1412_final_static_validation.json` og
`analysis/firmware1412_final_release_validation.json`.

Serverpakke: `update_server/saiv_instrument_terminal_v1.4.12_oct2026.zip`,
`readme_v1.4.12.txt` og `latest.json`. Last opp alle tre, latest.json sist.
Pakken og alle kontrollsummer er laget på nytt. Rapport:
`analysis/update_server1412_validation.json`. Fortsatt usignert; ingen
serveropplasting, signering, commit eller push er utført.
Notatene nedenfor beskriver tidligere arbeidssteg.

## SIT 1.4.13 – riktig firmwarekanal for 3.1.2 / 3.3.0, 28. oktober 2026

Nyeste lokale leveranse er **SAIV_Instrument_Terminal_v1.4.13_Oct2026.exe**.
Brukeren ba om støtte for maskinvare 3.3.0 med kontroll av riktig variant.
Help > Firmware velger hw_3-1-2 eller hw_3-3-0 automatisk ut fra bekreftet
enhetsidentitet. USB-konfigurasjon og fersk enhetsavlesning må stemme;
manifestets maskinvare, BIN-filnavn og README-adresse bindes til samme kanal.
Ukjente revisjoner og kryssede varianter avvises. Ingen manuell overstyring.
Eksisterende backup, filverifikasjon og etterkontroll er beholdt.
Kundevendt filtrering dekker også interne instruksjoner i dagens servernotat.
Les `LES_MEG_Firmware_HW_1413.md`.

291 protokollkontroller og 30 Windows-kontroller bestod. Begge produkter på
begge revisjoner, feil variant og endret identitet er dekket. Produksjonens
WinINet-kode hentet 0.9.9S fra begge serverkanaler med riktige SHA-256 og
filtrerte kundetekster. GUI viste begge revisjoner og avviste oppdatering
uten tilkobling. Alle 15 kundefileksporter er byteidentiske med bevart 1.4.11;
flerfilflyt, enkeltfilflyt, feil, avbrudd og nye betingelser bestod.
GUI brukte egne kopier på privat skrivebord, minnestubber for register og
deaktivert serieportåpning. Ingen fysisk firmwareoppdatering er utført.
Samlerapport: `analysis/firmware1413_release_validation.json`.

Bygg: `analysis/build_single_exe_1413.py`, innebygd `SIT_Import153.dll`.
EXE SHA-256: `0c6285311c3413bf0b0f5d7d6d9d9434c72d6402d6812fa4e2bb073d231c59e9`.
Native runtime er bare endret ved DLL-referanser, About/versjon og kontrollsum.
Beregnings- og batchkilder er uendret. Forrige kilde er arkivert i
`analysis/reference/sit_import_v1412`, og historisk 1.4.12-bygg bruker arkivet.
Tidligere leveranser er beholdt. Programmet er fortsatt usignert.

Serverpakke: `update_server/saiv_instrument_terminal_v1.4.13_oct2026.zip`,
`readme_v1.4.13.txt`, `latest.json`. Se `update_server/LAST_OPP_1.4.13.md`;
last opp latest.json sist. Forrige peker: `latest_v1.4.12.json`.
CRC, eksakt innhold, versjon og hasher kontrollert i
`analysis/update_server1413_validation.json`. ZIP SHA-256:
`95bf5f8828022e53f66711e5e97cde2a1ad3b6236b119f8db2cd52d2ad16f4e9`.
Oppdateringsinstallasjon av selve SIT er ikke kjørt på nytt. Ingen
serveropplasting, signering, instrumentkommando, commit eller push.

## Serverpakke 1.4.12 klargjort, 28. oktober 2026

Brukeren ba om serverversjon av 1.4.12 med flerfilkonvertering. Lokal pakke:
`update_server/saiv_instrument_terminal_v1.4.12_oct2026.zip`,
`readme_v1.4.12.txt` og `latest.json`. Last opp ZIP og versjonsnotat først,
latest.json sist. Se `update_server/LAST_OPP_1.4.12.md`.

Pakken inneholder byteidentisk testet 1.4.12-EXE, engelsk kundetekst og
miniz/GSW-lisenser. EXE-en er fortsatt **usignert**; brukeren ba nå om pakken
før signering er ferdig. Ingen signering eller serveropplasting er utført.
Ved senere signering må ZIP og manifest bygges på nytt med nye kontrollsummer.
Forrige peker er bevart som `latest_v1.4.11.json`; eldre pakker er beholdt.

Bygg: `analysis/prepare_update_server_1412.py`. Kontroll:
`analysis/update_server1412_validation.json`. ZIP-CRC, eksakt innhold,
EXE-/ZIP-hash, versjon 1.4.12.0 og kundetekst er kontrollert.
ZIP SHA-256: `050af334d9d09ee40cf688aac549420180d819186cfd36057b35d3cf9ec468ab`.
Eksisterende flerfiltester gjelder samme EXE; oppdateringsinstallasjon er ikke
kjørt på nytt for denne pakken. Ingen instrumentoperasjon, commit eller push.

## Signering og overlevering, 26. oktober 2026

Les [dagens sammendrag](DAGSNOTAT_2026-10-26.md). Azure Artifact Signing-kontoen
`saivsigning` er opprettet med Basic i North Europe, ressursgruppe
`rg-saiv-signing`. Public Organization-validering for SAIV AS står sist som
In Progress. Personlig ID-kontroll av representanten gjenstår; brukeren tar
med fysisk førerkort 27. oktober. Ingen sertifikatprofil eller signering ennå.
Brukeren ønsker flere SAIV-programmer signert i samme periode og vil senere
avslutte signeringskontoen, men beholde Azure-abonnement og identitetsgodkjenning.
Ingen sletting nå. Alle signaturer skal tidsstemples. Ingen kunder har tatt
i bruk 1.4.12, så signert leveranse skal fortsatt ha versjonsnummer 1.4.12.
Ny serverpakke lages etter signering og testes mot eksisterende oppdaterer.
Brukeren har nå bedt om sammendrag, commit og push; notatene nedenfor om
«ingen commit eller push» beskriver tilstanden før denne Git-leveransen.

## SIT 1.4.12 – flere filer i Convert, 26. oktober 2026

Nyeste lokale leveranse er **SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe**.
Les `LES_MEG_Batch_1412.md`. Convert-knappen og File-menyen lar brukeren velge
flere TXT/CSV-filer med Ctrl/Shift. Ved flere filer velges utmappe; beregningsvalg
gjenbrukes for samme instrumenttype og kolonneoppsett. GPS og manglende T/S/AP
etterspørres per fil. Hver fil eksporteres separat som `_SIT.txt`; eksisterende
filer beholdes med nummerert nytt navn. Eget vindu viser animert fremdrift,
resultat per fil og Cancel remaining. Feil i én fil stopper ikke de andre.
Enkeltfilvalg beholder tabell/kurve, Export all fields og Import to SD2.

Alle de 15 filene i `data/dataFormCoustomer` er testet: komplette eksporter er
byte-identiske med individuell Convert i bevart 1.4.11, og kildefilenes SHA-256
er uendret. Eksisterende utfil, enkeltfilflyt, ugyldig fil, avbrudd før og under
jobben samt nye spørsmål om manglende betingelser er kontrollert. Delphi-trådens
x87-kontrollord overføres til arbeidertrådene for identisk avrunding.
GUI-testene bruker egne kopier på privat skrivebord, minnestubber for registeret
og sperret fysisk portaapning. Resultat: `analysis/batch1412_release_validation.json`.
Detaljrapport: `analysis/runtime_test/batch1412/1793017739114155100/report.json`.

Bygg: `analysis/build_single_exe_1412.py`. En-EXE med `SIT_Import152.dll` innebygd.
SHA-256: `14fb2a3c451b2c620e3e18394a5f59b0b9d438655f1e693188a77f5823f2c896`.
Forrige 1.4.11-EXE og kilde er bevart; byggskriptet for 1.4.11 bruker nå
`analysis/reference/sit_import_v1411`. Beregnings- og firmwarekilder er uendret;
statisk kontroll begrenser runtime-endringene til Convert-inngang, DLL-navn,
About/versjon og PE-størrelser/kontrollsum. Quick guide er oppdatert.
Ingen instrumentoperasjon, serverpublisering, commit eller push er utført.
Utgaven er usignert mens SAIV oppretter Azure-signering.

## Firmwarekandidat 1.4.11, 13. september 2026

**Kundevisning rettet, fortsatt 1.4.11:** Intern servicetrafikk fanges av firmwarekontrollen, men hoppes over i terminalvisningen under firmwarejobber. Loader og resultat beholdes i eget vindu; rå servicesvar vises ikke ved feil. Full P-til-R-test bestod med uendret terminalhistorikk gjennom hele jobben: `analysis/runtime_test/firmware1411/physical/1789337799238129300/report.json`. Deretter ble kun kundevendt filtrering av serverens README lagt til og fysisk kontrollert: `analysis/runtime_test/firmware1411/physical/1789337946490848600/report.json`. Siste EXE SHA-256: `fc3c03396041d9068e7cdfdd156da6c771d623f84768b56f561a26f4d1efb46b`. Serverpakken er bygget på nytt med denne EXE-en; last opp ZIP, readme og latest.json på nytt, sistnevnte sist. Tidligere testet EXE/pakke er bevart under `analysis/reference/firmware1411_before_quiet`. Ingen 1.4.12 er laget. Se AGENTS.md for fast policy om intern servicemeny.

Serverpakke 1.4.11 klargjort 14. september: `update_server/saiv_instrument_terminal_v1.4.11_sept2026.zip`, `readme_v1.4.11.txt` og `latest.json`. Last opp latest.json sist til saiv.no/software. Filnavn/URL-er bruker små bokstaver i tråd med brukerens server. ZIP inneholder byteidentisk fysisk testet EXE, README og lisenser. CRC, innhold, EXE-versjon og SHA-256 er kontrollert; rapport `analysis/update_server1411_validation.json`. Forrige peker er bevart som latest_v1.4.10.json. Les `update_server/LAST_OPP_1.4.11.md`. Ingen serveropplasting fra agenten.

**Sluttest bestått 14. september 2026:** Brukeren satte SN107 tilbake til P. Uendret sluttbygg (`e92f36b0bb26b90e36296ea1c9066fe641539c76eaf85f56352c970047857dff`) fullførte hele P-til-R-løpet med «Firmware update successful». Fra FWU-start til suksess tok det 111,6 sekunder. VER og INI viste R, FWUST var CLEAR, update-mappen var tom, øvrige config-filer og alle andre INI-verdier var bevart. Ingen ekstra oppryddingsreset eller manuell inngripen var nødvendig. Rapport: `analysis/runtime_test/firmware1411/physical/1789336734610481300/report.json`. COM11 er frigitt. Den tidligere manglende komplette retesten er dermed utført; SAIV110 er fortsatt ikke fysisk testet.

Branch `feature/firmware-update`. Utviklingskandidat: `SAIV_Instrument_Terminal_v1.4.11_Sept2026.exe`. Les `LES_MEG_Firmware_1411.md` og `osu107Doc/TIL_OPPDATERINGSAGENT_0.9.9R.txt`. Tidligere leveranser og 1.4.10-kilde er bevart. SIT har fysisk oppdatert OSU107 SN107, HW 3.1.2, fra P til R på COM11 med USB tilkoblet hele tiden.

Help > Firmware sjekkes bare manuelt. Disk/COM matches via fysisk USB-identitet. BIN kopieres som update/osu_m_update.bin, flushes og verifiseres før CFG/FWU. Kjørende firmware leses fra fersk lokal meny, også uten DTR-info. Enheten fjerner BIN selv; én ekstra reset tillates hvis update-mappen ikke er tom. Etter verifisert ny firmware slettes **bare config/system.ini**. Øvrig config/kalibrering beholdes og kontrolleres bytevis; innstillinger og ny versjon verifiseres etter regenerering. PC-backup beholdes.

Dialogen har animert indikator, medgått tid, gjeldende trinn og permanent USB-beskjed under oppdatering. Hele BIN leses tilbake og sammenlignes før FWU; bekreftet byteantall vises. Fersk lokal meny og VER må stemme. FWUST må være CLEAR, og update-mappen må være tom før og etter system.ini-regenerering. Manuell kontroll av allerede installert serverversjon verifiserer også system.ini og opprydding uten ny flashing eller reset.

Første R-test installerte R, firmware fjernet BIN og frigav FWU-låsen, og SIT regenererte bare system.ini. En SIT-feil i siste kontroll (CFG før lokalmeny etter omstart) ga ingen suksessmelding i første forsøk; denne rekkefølgen er rettet og full retest er nå bestått som beskrevet over. Original testlogg er bevart: `analysis/runtime_test/firmware1411/physical/1789335812151538500/report.json`; diskverifisering ligger i samme mappe. Se `analysis/firmware1411_validation.json` for sluttbyggets hash og testresultater.

R-serverpakken er verifisert: latest.json, readme.txt og BIN svarer HTTP 200 og matcher lokal pakke. R-BIN: 635648 byte, SHA-256 `d557327dae4af7bc90ef2555c800184a6cc08296622cada0f6fc347d30af24a6`. Rapport: `analysis/runtime_test/firmware1411/server/validation_R.json`. Q-testens oppryddingsfeil er historisk og beskrevet i `osu107Doc/SIT_FIRMWARE_TEST_2026-09-13.md`. Ingen serveropplasting, firmwarekildeendring, commit eller push fra SIT-arbeidet.

## Start her neste gang

1. Les dette notatet og brukerens nye oppgave.
2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe**. Les [LES_MEG_Batch_1412.md](../LES_MEG_Batch_1412.md). Kunden trenger fortsatt bare EN EXE.
3. Les relevante dokumenter og byggskript i `analysis` før patching. Mange skript krever en bestemt eldre kildefil og SHA-256; de kan ikke ukritisk kjøres på siste utgave.
4. Lag en ny programkopi og behold tidligere leveranser. Verifiser relevante endringer og lever den konkrete EXE-filen.

Vi har ikke original Delphi-kildekode. Arbeidet består av analyse og patching av en 32-bits Delphi Windows-EXE: maskinkode, PE-ressurser og DFM-skjemaer. Dokumentasjonen om instrumentfirmware er en separat kilde og må ikke forveksles med Windows-koden.

## Git-leveranse, 10. september 2026

Brukeren har bedt om commit og push. Aktiv gren er `main`, med `origin/main` som upstream; grenen inneholder allerede SIT 1.4.3. Eldre notater om at main beholder 1.3.6 er historiske. Leveransen omfatter Studio 0.3.0/0.3.1, SIT 1.4.4/1.4.5, kildearkiver, bygggrunnlag og testdokumentasjon. Refererte bilder fra SIT-gjennomgangen bevares; fulle skrivebordsbilder og byggmellomfiler holdes lokalt. Git-push publiserer ikke oppdateringspakken paa saiv.no.

## Serverpakke 1.4.10 klargjort, 10. september 2026

Brukeren ba om ny release i update_server for egen opplasting. Pakken inneholder den testede SIT 1.4.10-EXE-en, versjonsnotat med endringene siden 1.4.3 og miniz/GSW-lisenser. Last opp SAIV_Instrument_Terminal_v1.4.10_Sept2026.zip, README_v1.4.10.txt og latest.json sist til saiv.no/software. Se update_server/LAST_OPP_1.4.10.md. Eldre pakker er beholdt; gammel peker arkivert som latest_v1.4.3.json.

ZIP-CRC, EXE-hash, versjonsressurs 1.4.10.0 og pakkeinnhold er kontrollert. Eksisterende 1.4.1-oppdateringshjelper har installert den faktiske serverpakken p? en isolert testkopi: feil SHA avvist, samme filsti bevart, byteidentisk backup og omstart uten administrator. Rapporter: analysis/update_server1410_validation.json og analysis/runtime_test/update1410/install_validation.json. Ingen serveropplasting, instrumentkommandoer, commit eller push.

## Nyeste SIT-leveranse: 1.4.10 - S og instrumentets salinitetsmetode, 10. september 2026

Brukeren ba om å rette salinitetsforklaringen i selve programmet. Quick guide sier nå uttrykkelig at SD208 beregner S fra C/T/P med PSS-78. S brukes i symbolforklaringer og eksempler; SP forklares én gang som fagbetegnelse for samme praktiske salinitet. Instrumentets lagrede S skilles fra ny beregning i Convert, og guiden forklarer at Convert ikke endrer instrumentets metode. Les [LES_MEG_Salinity_Guide_1410.md](../LES_MEG_Salinity_Guide_1410.md).

En-EXE bygget og alle 26 guideemner kontrollert i faktisk program, inkludert full tekst, tastatur, rulling og lukking. Kun guide og programversjon endret. Tidligere 1.4.9-EXE og kilde bevart i analysis/reference/sit_import_v149. Bygg: analysis/build_single_exe_1410.py. Rapport: analysis/salinity_guide1410_release_validation.json. Ingen instrumentkommandoer, commit, push eller serverpublisering.

## SIT-leveranse: 1.4.9 - enklere brukerguide, 10. september 2026

Brukeren ba etter omstart om å fortsette med en enklere guide som handler om brukerens målinger og SIT-valg, uten omtale av hva som fantes i koden. Quick guide har nå 26 emner med betjening, praktiske metodevalg, enheter og korte eksempler. Temperatur og OSU107 er forenklet. Detaljert formeldokumentasjon er bevart utenfor guiden. Les [LES_MEG_Simple_Guide_149.md](../LES_MEG_Simple_Guide_149.md).

En-EXE bygget og alle 26 emner kontrollert i faktisk program: full tekst, tastatur, rulling, minimumsstørrelse og lukking. Konteksthjelpens emnemål er kontrollert. Beregningskilder og tidligere 1.4.8-EXE er uendret; runtime-kontroll inngår i bygget. Rapport: analysis/simple_guide149_release_validation.json. Ingen instrumentkommandoer, commit, push eller serverpublisering. Bygg: analysis/build_single_exe_149.py. Historisk kilde bevart i analysis/reference/sit_import_v148.

## SIT-leveranse: 1.4.8 - systemvurdering, 10. september 2026

Quick guide har nå 33 emner. «System evaluation» gir en kort, enkel anbefaling; «System: measurement quality» forklarer kvalitet, fordeler og informasjonstap gjennom CTD/STD, SIT og OSU107. Start here viser til vurderingen. PSS-78/EOS-80/TEOS-10 og Steinhart-Hart, Kelvin-konstant og temperaturskala holdes tydelig fra hverandre. Les [LES_MEG_System_Evaluation_148.md](../LES_MEG_System_Evaluation_148.md).

Kildegrunnlaget omfatter den nye asmCTDdoc-rapporten og OSU107-handover-notatene. Ingen udokumentert tallfesting av OSU107-kanalnøyaktighet eller årstall for temperaturendring. Ingen målefil, sted eller installasjon oppgis i guiden. Formler og metodeidentifikator 1.4.7 er bevart; denne utgaven endrer hjelpetekst og programversjon.

Kontrollert: fire firmware/SIT-salinitetseksempler, 60 lydhastighetssammenligninger, uendrede beregningskilder og native runtime, samt alle 33 emner i faktisk en-EXE med full tekst, rulling, tastatur, lukking og kjøring uten administrator. Ingen instrumentkommandoer. Rapport: analysis/system_evaluation148_release_validation.json. Historisk 1.4.7-kilde er bevart i analysis/reference/sit_import_v147.

## SIT-leveranse: 1.4.7 - formelguide og metodevalg, 10. september 2026

Brukeren ba om dokumentasjon av faktiske SD200W/SIT-formler, regneeksempler uten m?lefil/sted, offentlige referanser og valgbare metoder i Convert. 1.4.6 utvidet guiden til 29 emner og er bevart som mellomleveranse; 1.4.7 har 31 emner inkludert akustikkreferanse og GSW-lisens, pluss egne metodevalg i Next-veiviseren og direkte konteksthjelp. Les [LES_MEG_Formulas_146.md](../LES_MEG_Formulas_146.md) og [LES_MEG_Conversion_Models_147.md](../LES_MEG_Conversion_Models_147.md).

Convert tilbyr original PSS-78, GSW PSS-78/Hill, SA/CT, eksplisitt temperaturskala, seks trykk-/dybdevalg, fire tetthetsvalg, fem lydhastighetsmodeller og SIT/GSW-oksygen med fire konsentrasjonsenheter. Valg av beregnet S fra C kan overstyre eksisterende S som kilde til avledede beregninger. T/S/AP/GPS og referansesammensetning/atlas gjennomg?s; metode og antakelser f?lger eksporten. PAR, OF og OT har sine dokumenterte enhetsregler, uten en oppdiktet FTU/NTU/FNU-faktor. Eldre CTD/STD-tekst med Date/Time/Interval kan n? brukes direkte i Convert; rekonstruerte tider merkes.

Den opprinnelige Delphi-kjernen er bevart. De nye modellvalgene gjelder Convert, ikke alle gamle Compute-/kalibreringsmenyer. SIT-lignende profilintegrasjon f?lger kontrollert normalregel; alle native maskerings-/offsetgrener er ikke rekonstruert. Nytt er ogs? kontroll av Kelvin-handlerens 273,16/273,15 og profilnormalregel; tidsskille per firmware/serienummer er fortsatt uavklart. Se oppdaterte FORMELKARTLEGGING/FORMELKONTROLL.

Bygg: analysis/build_single_exe_147.py fra bevart 1.4.6-runtime. GSW-C er statisk lenket, med uendrede kildefiler/lisens og 3.06.16-atlasdata. Kunden trenger fortsatt bare ?n EXE. 1.4.5-/1.4.6-kilden er arkivert i analysis/reference/sit_import_v145 og sit_import_v146; historiske bygg bruker arkivene. Originaler og tidligere leveranser beholdes.

409 numeriske/integrasjonstester inkluderer native regresjoner, offentlige GSW-eksempler, atlasreferanser, dyp til 4000 dbar, profiler, enheter, input-/feilgrenser, parser og innstillingsmigrering. Sluttrapport for faktisk EXE, alle 31 guideemner, Next/hjelp/eksport/SD2-gjen?pning og filhasher: analysis/models147_release_validation.json. SD2 beholder moderne feltnavn og verdier uten ? legge til automatisk feilmerket SIT-lydhastighet eller ekstra EOS-80-kolonne. Ingen instrumentkommandoer, fysisk kalibreringsvalidering, serverpublisering, commit eller push i dette arbeidet.

## Tidligere SIT-leveranse: 1.4.5 - instrumentikon i About, 10. september 2026

Brukeren ba om at det gamle instrumentbildet i Help > About skulle erstattes med det nye ikonet. About bruker naa samme 64-pikslers instrumentikon som icon/ctd_in_Cage.ico. Bildet er kodet som klassisk DIB for den gamle Delphi-visningen; RGBA-pikslene er beholdt. Resten av About og Quick guide er bevart. Les [LES_MEG_About_Icon_145.md](../LES_MEG_About_Icon_145.md).

Leveranse: **SAIV_Instrument_Terminal_v1.4.5_Sept2026.exe**, fortsatt en EXE. Visuelt kontrollert i kjorende SIT: hele ikonet, versjonstekst, krediteringer og knapper er synlige. About lukkes normalt; Quick guide og Update software fungerer. Rapport: `analysis/about145_release_validation.json`. Ingen instrumentkommandoer eller oppdateringshenting i testen. Bygg: `analysis/build_single_exe_145.py`, ressursendring i `analysis/patch_about_icon145.py`. 1.4.4-kilden er bevart i `analysis/reference/sit_import_v144`, og historisk bygg bruker arkivet. Tidligere EXE-er er beholdt. Ingen serveropplasting eller push. Visuell gjennomgang av instrumentbruk er fortsatt utsatt til instrumenter er tilkoblet.

## Tidligere SIT-leveranse: 1.4.4 – Quick guide, 10. september 2026

Brukeren ba om en Quick guide også i original SIT, tilpasset SITs egne menyer og utseende. Help > Quick guide har nå ni korte engelske emner i et vanlig SIT-hjelpevindu, med emnevalg, tastaturbetjening og justerbar størrelse. Guiden fungerer offline og uten instrument. Les [LES_MEG_Quick_Guide_144.md](../LES_MEG_Quick_Guide_144.md).

Leveranse: **SAIV_Instrument_Terminal_v1.4.4_Sept2026.exe** (én EXE). Faktisk GUI-kontroll av alle emner, piltaster, Esc/Close/vinduskryss, gjenåpning, minimumsstørrelse og bevart Update software-meny bestått. Bilder kontrollert visuelt. Rapport: `analysis/guide144_release_validation.json`. Ingen instrumentkommandoer eller nettverkskall i testen. Instrument- og datakilder samt installerhjelperen er bevart; runtime har bare nye versjonsressurser/DLL-navn/sjekksum. Bygg: `analysis/build_single_exe_144.py`. 1.4.3-kilden er arkivert i `analysis/reference/sit_import_v143`, og det historiske bygget bruker arkivet. Tidligere EXE-er beholdt. Ingen publisering eller push.

Brukeren har ikke instrument tilgjengelig nå. En visuell gjennomgang av faktisk SIT-bruk er mulig, men skal **ikke lages før instrumentene er tilkoblet**. Kun tekstguiden er levert nå.

## Rettet Studio-leveranse: 0.3.1, 10. september 2026

Brukerens skjermbilde viste at vanlig oppstart uten måledata presset terminalen til høyre. Årsaken var ubetinget SameLine før valgfrie knapper. 0.3.1 retter dette. Tidligere test med demodata skjulte feilen.

Leveranse: **SAIV_Studio_v0.3.1_Sept2026.exe**. Les [LES_MEG_SAIV_Studio_031.md](../LES_MEG_SAIV_Studio_031.md). Normal oppstart uten demo/testtransport kontrollert visuelt og med måling av terminalbredden i tre vindusstørrelser, pluss demo-regresjon. Alle 1164 CTest-kontroller består. Ingen fysisk instrumentport brukt. Rapport: `analysis/studio031_release_validation.json`; skjermbilder: `saiv-studio/test-results/v031`. 0.3.0-kilden er bevart i `analysis/reference/saiv_studio_v030`, og tidligere leveranser er beholdt.

## Ny selvstendig Studio-leveranse: 0.3.0, 10. september 2026

Brukeren ba om å lage Studio nå, med samme enkle terminalbetjening som SIT, men et moderne utseende. Brukeren presiserte at nye filer ikke trenger SD2; lesing av gamle SD2 skal beholdes. Aktivt Studio-arbeid er dermed gjenopptatt etter tidligere pause.

Leveranse: **SAIV_Studio_v0.3.0_Sept2026.exe**. Les [LES_MEG_SAIV_Studio_030.md](../LES_MEG_SAIV_Studio_030.md). Rett i terminal, enkel knapperekke, ekte UART 7E1, Convert/Merge, Interval/TIME-DATE, CSV som standard, gammel SD2-lesing, tabell/grafer og dataverktøy. Nytt grensesnitt kopierer ikke Windows 98-utseendet. Det er fortsatt en Windows x64-utgave; Linux/Mac er ikke levert.

Bygget med `saiv-studio/build.cmd`. 182 kjerne-, 50 kompatibilitets- og 932 innstillingsprotokollkontroller består. Samlet GUI-test og skjermbilder under `saiv-studio/test-results/v030`; SHA-bundet leveranserapport i `analysis/studio030_release_validation.json`. Fysisk instrumentakseptanse og full SIT-paritet gjenstår. Original SIT-kilde/moduler/leveranser er beholdt, og Studio 0.2.0-kilden er arkivert i `analysis/reference/saiv_studio_v020`. Ingen publisering eller push.

## Kjorende SIT gjennomgaatt som GUI-fasit for Studio, 9. september 2026

Brukeren ba uttrykkelig om aa aapne SIT og undersoke selve programmet og menyene foer et nytt forsoek med saiv-studio. SIT 1.4.3 er naa faktisk startet paa det interaktive Windows-skrivebordet. 67 hovedmenykommandoer med undermenytre er registrert; 49 menykommandoer er aapnet/forsokt, dessuten alle seks Setup-faner, alle sju Convert-feltsteg i OSU107-filen, Merge med mappesoek og native/importert Multigraph. Klassisk SD2-testkopi og 79-raders loggerfil er brukt. Convert -> Import to SD2 er utfort til egen testmappe. Menyene endrer seg mellom klassiske og importerte data.

Les [SIT_GUI_GJENNOMGANG.md](SIT_GUI_GJENNOMGANG.md) for konkrete skjermbilder, vinduer, menytraer og avgrensninger. Raa bevis under analysis/runtime_test/sit_live_review. Verktoy: analysis/inspect_sit_live.py og analysis/build_sit_gui_review.py. Originale leveranser/data er beholdt; vanlig brukerregister var ikke isolert. Ingen instrumentkommandoer, utskriftsjobb eller oppdateringshenting ble startet av gjennomgangen. Dette er GUI-kartlegging, ikke full funksjonstest. På dette tidspunktet var ingen ny Studio-utgave bygget; se den nyere 0.3.0-leveransen over. Studios tidligere femsiders utforming skal ikke brukes som fasit for en tro SIT-gjenskaping.

## Tidligere lokal leveranse: 1.4.3 - forklaring ved oppdateringshaken

Brukeren bekreftet at oppdatering til 1.4.2 virket. 1.4.3 legger til engelsk tekst under Do not check for updates at startup: "Use Help > Update software to check for updates manually or turn this startup message back on." Vinduet har ekstra plass til forklaringen. Ingen endring i instrument- eller installasjonslogikk. Ny serverpakke i update_server. Bygg: analysis/build_single_exe_143.py. 1.4.1-kilden er arkivert i analysis/reference/sit_import_v141 slik at det eldre bygget bevares. Ingen serveropplasting. Brukeren ba om commit og push av update etter denne endringen.

## Tidligere lokale leveranse: 1.4.2 - testoppdatering

Brukeren ba om en nyere versjon for aa teste oppdatering fra 1.4.1. 1.4.2 har kun ny versjonsmerking, samme funksjoner og byteidentisk oppdateringshjelper. Nye brukere kan ogsaa bruke denne direkte, uten tidligere installasjon. Serverfiler i update_server er klargjort for 1.4.2; brukeren laster opp ZIP/README og latest.json sist. Start 1.4.1 for aa teste oppdatering, og kontroller etterpaa versjon 1.4.2 i programmet; gammelt filnavn beholdes. Les [LES_MEG_Update_Test_142.md](../LES_MEG_Update_Test_142.md). Tester under analysis/runtime_test/update142. Ingen serverendring eller push.

## Tidligere lokale leveranse: 1.4.1 - oppdateringssjekk og installasjon

Les [LES_MEG_Update_141.md](../LES_MEG_Update_141.md). Branch update. Oppstartssporsmaal foer nett, lagret av-hake og Help > Update software. HTTPS henter latest.json og README fra saiv.no/software. Numerisk versjonskontroll, README-popup og bekreftet Install update. ZIP hash/CRC og innebygd EXE-versjon kontrolleres. Innebygd native hjelper bytter kundens EXE paa samme sti med samme navn, beholder backup og starter igjen. UAC bare ved manglende skrivetilgang; beskyttet-mappe-grenen er ikke fysisk testet. Kunden trenger fortsatt bare EN EXE.

Serverens 1.4.0-filer er verifisert offentlig via HTTPS (200, byteidentiske, korrekt SHA256). GUI og installasjon er testet, og samme oppdateringskode i en isolert eldre testklient har faktisk hentet og installert 1.4.0 fra serveren, med Nei/Ja, backup og omstart. Full rapport i analysis/runtime_test/update141. Ny serverpakke 1.4.1 klargjores lokalt; opplasting gjores av brukeren. 1.4.0 og eldre trenger manuell forstegangsoppgradering til 1.4.1. Ingen serverendring eller push er gjort av oss.

## Tidligere lokale leveranse: 1.4.0 - klokken settes en gang

Les [LES_MEG_Clock_140.md](../LES_MEG_Clock_140.md). Brukeren observerte dobbel klokkesetting paa COM11. Fysisk test bekreftet at 1.3.9 skrev SD200 to ganger ved kompensasjonsforsok, deretter OSU107 en gang. 1.4.0 beregner minutt/sekund etter overfort dato/time-prefiks og kompenserer gjenstaaende tegn med maalt overforingstid. Automatisk andre skriving er fjernet; uavhengig kontrollavlesning beholdes. COM11 fysisk test paa levert EXE bekrefter EN SD200-skriving og EN logger-skriving, begge verifisert GMT. Intervall ikke endret. 932 protokollkontroller, 20 native/ASLR-kontroller og GUI-kontroll. Kilde139 arkivert, gamle leveranser beholdt. Ingen push.

## Tidligere lokale leveranse: 1.3.9 - Interval og TIME/DATE

Les [LES_MEG_Interval_Time_139.md](../LES_MEG_Interval_Time_139.md). Nye knapper Interval (Alt+I) og TIME/DATE (Alt+A), Print flyttet til tidligere Setup-plass og Setup under Save text. Download/Interval/TIME krever akseptert Detect paa aktiv port. SAIV110 har samme elleve intervallvalg som SD200, ingen fritekst (brukerens uttrykkelige presisering).

SD200 bruker original I/Y/valg/CR-dialog og S-klokke. OSU107 bruker SD200-intervallet; begge klokker settes og kontrolleres separat, SD200 foerst og logger X deretter. SAIV110 setter loggerklokke med X og intervall via valgt USB config/system.ini, bevart originalfil, flush, 10 sekunder og U med endelig OK SAIV110_UPDATE_CONFIG. Logger etterlates stoppet. PC-klokke LT eller GMT/UTC, ingen hardkodet tidssoneforskyvning. Bevarer ekte UART og eksisterende serialport/terminalmottak.

Protokoll-, native gateway- og GUI-tester samt import/graf-regresjoner dokumenteres i settings139_release_validation.json. Brukeren autoriserte og vi utfoerte fysisk test: SD204 SN1756 COM7 (2sec beholdt, klokke PC-GMT) og OSU107 SN107 med SD208 SN1456 COM11 (1sec beholdt, begge klokker PC-LT). Tilbakeavlesning verifisert. SD200-klokkeavlesning kontrolleres foer menynavigasjon; maalt overfoeringsetterslep kan korrigeres med ett nytt forsoek. SD200 vekkes med avgrenset I-sekvens, TX stopper ved RX. Faktisk Change GMT/LT: Y/N stoettes. Surface er kun protokoll-/GUI-testet; OSU-modus er ikke endret. Se physical_gui_validation.json og physical_preflight.json under analysis/runtime_test/settings139. Originale formler og UART/refresh-kode beholdt. Import v1.3.7 arkivert og historisk bygg oppdatert til arkivet. Egen leveranse paa feature/import-all-fields, main 1.3.6 beholdt, ingen push.

## Tidligere lokale leveranse: 1.3.8 - hurtigtaster og Log-knapp

Download beholder &Download (Alt+D), Detect er D&etect (Alt+E). Log-knappen har Visible=False og TabStop=False; komponent, callback og all loggkode beholdes. Dette er kun endringer i TFORM1-ressursen og versjonsinformasjonen, bygget fra bevart 1.3.7-runtime. SIT_Import137.dll er byteidentisk og fortsatt innebygd i en enkelt EXE; importfunksjonene er uendret.

Bygg: analysis/build_single_exe_138.py. Faktisk enkelt-EXE kontrollert uten administratorrettigheter: riktig Download/Detect-tekst, Log skjult. Ingen instrumentkommandoer sendt. Rapport: analysis/runtime_test/buttons138/validation.json. Bygget kontrollerer alle ressursendringer og at eksisterende programbytes ellers er uendret. Eldre leveranser beholdt. Egen commit paa feature/import-all-fields; ingen push.

## Siste lokale importleveranse: 1.3.7

Arbeidet paa feature/import-all-fields er gjenopptatt etter brukerens beskjed og inkluderer main 1.3.6. Brukeren bekreftet at Download-rettingen virker. Nytt omfang inkluderer begge oppgitte _C-filer OG _merged-3, samt direkte Import to SD2 ved siden av Export all fields i Convert. Main 1.3.6 er sikret i 48ae885; integrasjonsmerge paa importgrenen d011d51.

Import CSV/TXT gjenkjenner FIELDS/Convert/Merge og bruker gammel ASCII-import ellers. Native SD2/RF2 og relevante OX2/OP2 lages sammen med SF2 som bevarer hele kildeformatet. Open SD2 laster SF2 igjen; kontrollverdi mot SD2 oppdager feil kombinasjon. Filgruppen maa beholdes samlet. Vanlige grafknapper/menyer og Multigraph bruker den originale native Multigraph-komponenten for importerte felt, med opptil ti valgbare kanaler. Master/M1/M2-navn bevares. Tidsgraf bruker faktiske radtider; trykk og dybde skilles. Alle felt vises/eksporteres fra datalisten.

Tre brukerfiler (79/3/79 rader) er kontrollert mot native punktarrayer, feltbytte, lister og gjenapning. Legacy 43-raders input gir fire native filer byteidentiske med originalimport. Direkte Convert-import bevarer Fahrenheit-valg og valgte verdier. Salinitet/lydhastighet/tetthet bruker originale rutiner naar native felt mangler; konverterte verdier beholdes. UART/Download/formelbytes uendret; native hook-register/stack/ASLR kontrollert. Se release- og GUI-rapporter nevnt i LES_MEG_Import_All_Fields_137.md.

Visuelle skjermopptak var svarte/utilgjengelige i Windows-oekten; kontroller og faktiske native punktdata er verifisert, men brukerens visuelle test gjenstaar. SF2 er et importgrunnlag, ikke synkronisert med senere redigering i de gamle native redigeringsverktoeyene. Native datogren er begrenset til 1981-2079. Tidligere leveranser og 1.3.6-kilder er bevart. Ingen push.

## Tidligere lokale leveranse: 1.3.6 - separat Import og logger-Download

Gjenopprettet original Import ASCII som File > Import CSV/TXT; Convert CSV/TXT forblir separat. Native sample 26090606_18.11.51.txt gir 43 maalinger og SD2/RF2/OX2/OP2 byteidentiske med originalimport. Convert av eldre tekst gir henvisning til Import. `_C`/`_merged` til native SD2 er fortsatt senere arbeid, ikke inkludert.

Bekreftet Autodetect OSU107/SAIV110 brukes for samme COM-port ved Download. Gammel CTD/Burst-tekst skannes ikke i loggergrenen og loggerlinjer gaar ikke gjennom CTD-parseren. Eksisterende refresh-handshake og SD200/Log viderefores. PAR/OXR normaliseres i FIELDS og Full foer valg/beregninger/preset-signatur; OX fortsatt separat. CTD-formelbytes uendret fra 1.3.2.

Tester: 43 samplemaalinger + bytekontroll av fire native filer, reell enkelt-EXE og separate menyer, 53 alias-, 35 Fahrenheit-, 263 preset-, 2054 GUI-verdi-, 46 native/ASLR- og 15 protokolltester bestod. Ingen fysisk instrumenttest. Se LES_MEG_Import_Download_136.md og analysis/native136_validation.json. Bygg build_single_exe_136.py. 1.3.5-kilden arkivert, tidligere leveranser beholdt. Arbeid paa main; feature/import-all-fields fortsatt pauset. Ingen push.

## Tidligere lokale leveranse: 1.3.5 - Fahrenheit og PAR-enhet

T-siden tilbyr Fahrenheit som egen T_degF-kolonne. Haken for original T styrer om Celsius ogsaa beholdes. Standard fortsatt Celsius. Fahrenheit beregnes etter sensorberegningene; disse bruker fortsatt Celsius. PAR-forklaringen viser output-enheten micromol photons/(m2*s), med riktige tegn i GUI. Inngangsarealenhet maa fortsatt velges ved PAR-konvertering.

Valget huskes: nytt preset-format SIT choices 2 leser ogsaa choices 1 fra 1.3.4 (Fahrenheit av). Register/signatur uendret. 35 Fahrenheit-/kompatibilitetstester, 263 preset-tester og 2054 GUI-verdikontroller bestod. Omstart/gjenbruk, Celsius beholdt/utelatt, grafetikett og PAR-tekst er kontrollert. Skjermbilder og rapport under analysis/runtime_test/fahrenheit135. CTD-formelbytes 0x10A000-0x10CFFF er identiske med bevart 1.1.3. Brukeren spurte spesielt om samsvar med gamle SD200W-formler; salinitet/lydhastighet/tetthet bruker fortsatt originalrutinene, Fahrenheit er et nytt tillegg.

En-EXE og automatisk AppData-oppsett viderefores. Bygg analysis/build_single_exe_135.py, DLL SIT_Import135.dll. Kildearkiver sit_import_v134 og sit_single_v134, eldre bygg peker dit. Les LES_MEG_Fahrenheit_PAR_135.md. Tidligere leveranser beholdt. Ingen ny fysisk instrumenttest eller GitHub-push.

## Tidligere lokale leveranse: 1.3.4 - gjenbruk av konverteringsvalg

Etter vellykket Convert lagres kolonnevalg per instrumentfamilie og eksakt kolonneliste/rekkefolge, med PAR-enhetsmetadata. Filnavn, serienummer, dato og maaleverdier ignoreres. Neste passende fil gir Ja/Nei/Avbryt med dato og forrige filnavn. Ja gjenbruker konverteringer/behold-valg, Nei gir vanlig Next-veiviser. Kun vellykket beregning oppdaterer historikken. Skadet historikk gir vanlig veiviser.

GPS og manuelt oppgitte manglende T/S/AP overfores ikke automatisk til en ny fil: GPS-side og bare manglende betingelser vises ved behov. Dette var den oppgitte standardantakelsen mens valgfritt sporsmaal til brukeren stod ubesvart. Lufttrykk fra den nye filen brukes. Lagring: HKCU/Software/MHP/SdInstr/ConvertPresetsV1, uavhengig av versjonscachen. Gjelder ny logger/FIELDS/Full-veiviser; native APB5-gren uendret.

259 lagrings-/signaturtester, GUI-omstart/gjenbruk, ulike oppsett, ny GPS, manglende betingelser, Ja/Nei/Cancel, beregningsfeil og korrupt historikk bestod. 4108 Merge-verdier og GUI-regresjon bestod. Visuelt kontrollert reuse_prompt.png under analysis/runtime_test/presets134. Tester bruker isolert historikk og ikke-elevaterte oppstarter/runtime. Ingen ny fysisk instrumenttest eller GitHub-push.

Bygg analysis/build_single_exe_134.py. Kilde sit_import/presets.h og presets_ui.inc med integrasjon i wizard.inc/sit_import.cpp. conversions.inc uendret. En-EXE, siste COM-port og automatisk AppData-reparasjon viderefores. Kildearkiver sit_import_v131 og sit_single_v133 er opprettet, gamle bygg peker dit. Eldre leveranser beholdt. Les LES_MEG_Convert_Presets_134.md.

## Tidligere lokale leveranse: 1.3.3 - en EXE med automatisk oppsett

Kunden trenger bare SAIV_Instrument_Terminal_v1.3.3_Sept2026.exe. Forste start legger innebygde runtime/DLL i brukerens LocalAppData/SAIV_IT/1.3.3_23c455263801. De beholdes og gjenbrukes; manglende/skadede filer gjenopprettes automatisk. Brukeren presiserte at automatisk oppsett ved forste start/manglende DLL er onsket, og at opprydding ikke er nodvendig.

Ingen administratorrettigheter kreves. Explicit asInvoker, og tester bekrefter TokenElevation=0 for begge prosessene, inkludert reparasjon. Institusjoners egne blokkeringsregler kan fortsatt kreve IT-godkjenning; et lokalt mappevalg er ikke lagt til fordi AppData allerede fungerer uten admin. Signering fortsatt utsatt.

Merge-eksport og Convert-veiviser fra faktisk enkeltfil testet. 4108 eksportverdier bestod. Flytting/nytt navn/norske tegn, gjenbruk uten omskriving, manglende og skadet DLL, manglende runtime og samtidige oppstarter bestod. Rapporter analysis/runtime_test/single133/. Bygg analysis/build_single_exe_133.py, kilde sit_single/. Innebygd runtime er 1.3.2 med kun versjonsressurser/sjekksum endret; DLL identisk med 1.3.1 og dens merge-header viser fortsatt modulversjon 1.3.1. Ingen ny fysisk instrumenttest eller GitHub-push. Tidligere leveranser beholdt. Les LES_MEG_Single_EXE_133.md.

## Tidligere lokale leveranse: 1.3.2 - husk siste COM-port

Bekreftet COM-port lagres alltid ved Setup/Detect-OK, og eksisterende oppstartskode leser den ved neste start. Tidligere hoppet lagringen over naar Detect allerede hadde satt porten. Feilen er reprodusert med 1.3.1: aktiv COM7, lagret COM11. 1.3.2 lagrer COM7 og starter med COM7. Manuelt COM11 og ny omstart, samt Cancel uten endring, bestod. 16 x86-tester bestod.

GUI-testen brukte isolert register og deaktivert fysisk portaapning; Detect-tilstand gjenskapt med native portsetter. Ingen ny fysisk instrumenttest. Brukerinnstillinger uendret. Les LES_MEG_Last_COM_Port_132.md. Bygg: analysis/build_last_com_port.py fra hashbundet 1.3.1. Kode: analysis/last_com_port.s. Tester: analysis/test_last_com_port.py og analysis/check_last_com_port_windows.py. UART/G/formler og Convert/Merge uendret. Bruk fortsatt SIT_Import131.dll; merge-header viser modulversjon 1.3.1. Eldre leveranser beholdt, ingen GitHub-push.

## Tidligere lokale leveranse: 1.3.1 - ryddig Merge-header og Convert

9. september: Brukerens headerendringer er implementert. Forste linje viser versjon, toleranse, dato/tid-valg og M1/M2 matches. Resten har masterheader/kildebane og M1/M2-header/kildebane uten ekstra forklaringer. Ingen semikolon over FIELDS; innleste semikolon blir komma. De to syntetiske testkommentarene utelates fra resultatet. Testfilene er fortsatt syntetiske og uendret.

Ny hake ved toleranse: Include date/time from merged files, standard pa. Av fjerner bare tilleggsfilenes DATE/TIME (og aliaser), mens mastertid og Delta_seconds beholdes. Convert erstatter Import pa knappen og Convert TXT/CSV i File/filvelger. Les LES_MEG_Merge_131.md.

9679 tids-/verdikontroller, 4108 GUI-verdikontroller, 16 Merge- og 10 importhooktester bestod. Egen GUI-test bekrefter dato/tid av/pa, uendrede andre celler, headerrekkefolge, rene kildelinjer og nye navn. PrintWindow-bilde visuelt kontrollert: analysis/runtime_test/merge131/merge_printwindow.png. CTD-formelbytes uendret. Gamle leveranser bevart. Bygg: analysis/build_logger_import_131.py. 1.3.0-kilde arkivert i analysis/reference/sit_import_v130. Ingen fysisk instrumenttest eller GitHub-push.

## Tidligere lokale leveranse: 1.3.0 – Merge med mappeskanning

Ny Merge-knapp under Import. Masterfil med radvis DATE/TIME, valgfri toleranse 0.0–10.0 s (default 0), skanning av valgt mappe i bakgrunn og opptil to tilleggsfiler. Valgfri egen bindestrek-kolonne, default av; filen er alltid semikolonseparert. Nærmeste tidspunkt per masterrad, inklusiv grense og mikrosekundpresisjon; ved lik avstand velges tidligste tid, så første originalrad. Tilleggsrader kan gjenbrukes. Alle masterrader beholdes, manglende treff gir tomme tilleggsceller. M1_/M2_-prefiks, originale datoer/tider og signert Delta_seconds gir sporbarhet. Ingen interpolering eller sensoromregning.

12 syntetiske SAIV110-filer er laget først i data/saiv110, basert på brukerens originale SAIV110-format og OSU107-datoer. De dekker før/etter, få/mange, 0.5/5/10/10.1 sekunder og feil dato. Ved toleranse 0/0.5/10 s finnes 4/6/8 filer. Originalfiler er urørt.

Portabel ZIP-pakke er også pakket ut i en annen mappe og kjørt derfra: Merge og medfølgende testfiler virker (6 treffiler ved 0.5 s).

9679 uavhengige tids-/verdikontroller, 4108 verdikontroller av GUI-eksport, Windows-flyttest og 16 Merge-/10 Import-maskinkodetester bestod. Eksisterende import: 1430 verdikontroller bestod. Dialogen ble kontrollert visuelt med PrintWindow (vanlig desktop-skjermdump viste bakgrunn og brukes ikke som dokumentasjon). Gyldig bilde: analysis/runtime_test/merge130/merge_printwindow.png. Rapporter i merge130 og import130. 1.2.2-kilde arkivert under analysis/reference/sit_import_v122; gammelt byggskript peker dit. Bygg ny versjon med analysis/build_logger_import_130.py.

Merge-resultatet har nye dato-/tekstkolonner og åpnes ikke automatisk i den gamle grafimporten. Les LES_MEG_Merge_130.md for formatgrenser og videre arbeid. docs/merge_filer_dato_tid.md gjelder en annen implementasjon med andre koblingsregler og er bevart uendret. Ingen GitHub-push.

## Tidligere lokale leveranse: 1.2.2 – Import-knapp og valgfri lydhastighet

Import-knapp direkte under Download bruker den eksisterende mnuImportASCIIClick-hendelsen. Log/Print/Setup flyttes til Top 120/152/184; ingen kommunikasjonsrutiner endres. T-siden har Calculate sound velocity (m/s), på som standard når CTD-grunnlaget er komplett. OFF hindrer ny beregnet lydhastighetskolonne; innleste originalkolonner har egne behold-valg.

GPS-reservebreddegrad 45,508368287° er arvet fra SIT og er ikke en faktisk posisjon. Brukerens Google Maps-par er et format-eksempel. Ny import etterspør manglende salinitet og bruker ikke skjult 35. Se LES_MEG_Import_122.md. Windows-knapptest med tre filer, lydhastighet på/av, 1430 verdikontroller og 10 hooktester bestod. CTD-formelbytes er identiske. 1.2.1-kilden er bevart under analysis/reference/sit_import_v121; eldre byggskript peker dit. EXE/DLL/ZIP for eldre leveranser beholdes. Ingen GitHub-push.

## Tidligere lokale leveranse: 1.2.1 – reelle feltvalg og enheter

Alle sensorfelt har **Keep original … values**, på som standard. C kan konverteres til S; P kan konverteres til Real depth (meter), med separat originalkolonne og valgfri GPS-posisjon skrevet som egen linje i eksporthodet. Feltets navn og enhet er tydelige: C Conductivity (mS/cm), T Temperature (°C, Celsius), P Pressure (dbar), OF Fluorescence (µg/L), OT Turbidity (FTU), Par Photosynthetically Active Radiation, OX SAIV205 Oxygen (%), OxR RINKO Oxygen (%). AP er mbar/hPa; brukerens eksempel med 600 mbar/6000 m er korrigert til 600 bar/6000 dbar i forklaringen, uten å legge regneeksemplet i UI.

Real depth bruker original SITs Fixed position-ligning med EOS-80-tetthet fra S/T/P og gravitasjon fra breddegrad/trykk. Native rutiner gjenbrukes. GPS bruker ett Google Maps-felt (`60.3936119227684, 5.29588169849683`) med Maps-lenke og Paste-knapp. Koordinatparet lagres på egen linje i filhodet. Tolv parsertester bestod. Separat automatisert Paste-test ble hoppet over fordi Windows nektet privat window station; brukerutklippstavlen er urørt. GPS har desimalgrader og validerte grenser; uten GPS vises og dokumenteres SITs standardbreddegrad 45,508368287°. Seks numeriske native-sammenligninger bestod. Profiling-grenen er ikke implementert i loggergrenen.

PAR kan konverteres til µmol fotoner/(m²·s) etter eksplisitt valg av inngangsenhet: per m² gir ×1, per cm² gir ×10000. Sertifikatet alene bekrefter ikke arealenheten i filen, og brukeren har ennå ikke besvart det særskilt. Derfor brukes ingen skjult faktor. OX og OxR har uavhengige valg for prosent, mg/L, mL/L eller begge. Ekstra betingelsesdialog hoppes over når verdiene er tilgjengelige; bare manglende felt vises.

De 43 OF/OT-verdiparene i APB5 ble importert med original SIT og sammenlignet med OP2: ingen skalering ble funnet, og native kanalnavn angir µg/L og FTU. Download-meldingen er rettet fra «Preforming refresh off disks» til «Performing refresh of disks» i alle tre tekstkopiene. Kommunikasjonskoden er uendret.

Windows-testene gir 1430 verdikontroller, alle originalhaker på som standard, eksplisitt utelatelse av originalkolonner, to PAR-faktorer, begge oksygensensorer, GPS-hode, avvisning av feilinput og Avbryt. 22 parser- og 10 x86-regresjoner bestod. Les `LES_MEG_Import_121.md` og rapportene i `analysis/runtime_test/import121/`. Ny DLL har eget navn; 1.2.0 EXE/DLL/ZIP er beholdt. Kilden til 1.2.0 er arkivert i `analysis/reference/sit_import_v120/`. Fortsatt lokal leveranse, ingen GitHub-push.

## Forrige lokale leveranse: 1.2.0 – Import CSV/TXT

Ny menytekst er **Import CSV/TXT**, etter brukerens siste instruksjon. Både CSV og TXT vises i filfilteret; Burst beholdes. OSU107/FIELDS og Surface importeres i en ny Win32-modul som lastes fra EXE-mappen. Feltvalg kommer før beregning, OxR kan beholdes i prosent eller legges til i mg/L, mL/L eller begge. Par og andre originale verdier beholdes. CTD-resultatene bruker eksisterende SIT-rutiner; ingen formler eller kommunikasjonsrutiner er rettet/endret.

Loggerdata vises i et eget datavindu med tabell, tidskurve og tapfri FIELDS-eksport. Den gamle APB5-grenen er beholdt og kontrollert med 43 rader. Loggerdata er foreløpig ikke koblet til SD2/RF2/OP2-lagring eller hovedvinduets standarddybde-/profileksport. Full-støtten er testet med syntetiske eksempler, ikke med en faktisk Full-fil fra instrument.

Brukeren presiserte at de første 2–3 målingene kan være ute av synk før vanlig intervall; dette skal ikke beskrives som et problem med hele serien. Tidspunktene i filen bevares. OSU-filen blander CR og CRLF, som nå håndteres.

Kontroller: 22 parser-/konverteringstester, 10 x86-gren-/relokeringstester og 483 eksportverdikontroller. Windows-test importerte/eksporterte 79 OSU- og 3 Surface-rader, prøvde Avbryt og original APB5-import. Se `analysis/logger_import_manifest.json`, `analysis/check_logger_*.py` og `analysis/runtime_test/logger_*validation.json`. Tidligere EXE-er og originaldata er beholdt. Ingen GitHub-push.

## Historisk kartlegging før implementeringen: import og konvertering

Brukeren har lagt APB5, OSU107, Surface og gamle test-filer i `data`. APB5 kan importeres; OSU107 og Surface blir ikke gjenkjent. Første formatkartlegging er gjort i [IMPORTKARTLEGGING.md](IMPORTKARTLEGGING.md), med maskinlesbar rapport `analysis/import_format_inventory.json` og leseskript `analysis/map_import_formats.py`.

OSU107-eksemplet har 79 rader med CTD og ekstrasensorer. Surface har tre rader med Par/OxR/Tilt uten CTD. Kolonnenavn og individuelle tidspunkt må bevares. Brukeren har bekreftet Biospherical PAR og RINKO III. Kalibreringsarkene i docs er lest; se [SENSORKALIBRERING_IMPORT.md](SENSORKALIBRERING_IMPORT.md). Brukeren har senere avklart normal inngang som oksygenmetning 0–200 %, PAR beholdes uendret, og CTD-modus/OF/OT håndteres som før. Ingen volt-/kalibreringsspørsmål i normal flyt. Både FIELDS- og Full-format skal støttes. Ingen EXE-importrettelse er laget i denne fasen. Siste leveranse er fortsatt 1.1.3. Originalfiler er urørt.

## Navn og kontroll av konverteringsdokumentet

Brukeren har valgt SAIV IT eller SIT som kortnavn for SAIV Instrument Terminal. Dette gjelder samme program; eldre SD200W-referanser gjelder bevart kode og historiske filer.

`docs/konverteringer_og_eksport.md` er sammenlignet med SIT 1.1.3. Flere funksjonsvalg er like, men salinitet, oksygen, lydhastighet, reserveverdier og eksportflyt er ikke identiske. Syv numeriske sammenligninger er gjort mot EXE-rutiner. Den tidligere dokumentutgavens salinitetsformel gir 35 ved C=42,914 og T=10, mens SIT gir 39,9967. Behold derfor eksisterende CTD-beregninger som avtalt. Se [KONVERTERING_SAMMENLIGNING.md](KONVERTERING_SAMMENLIGNING.md). Ingen EXE er endret i kontrollen.

## Konverteringsdokumentet rettet med SIT som fasit

Brukeren ba om å rette `docs/konverteringer_og_eksport.md` for bruk i et annet program. Dokumentet er omskrevet med SITs salinitet, oksygen, enhetskonstanter, lydhastighet og tetthetsgrener, samt kartlagte dybdeformler og tydelige forbehold om uavklarte kallkjeder. Komplett Python-referansekode er inkludert i Markdown-filen. Det andre programmets eksportformater er skilt fra påstander om eksisterende SIT-eksport. Ingen programkode er endret.

`analysis/check_sit_conversion_document.py` leser koden direkte fra dokumentet: 31 kontroller mot registrerte EXE-resultater bestod. Rapport: `analysis/sit_conversion_document_validation.json`. Tidligere dokument er bevart i `analysis/reference/konverteringer_og_eksport_before_SIT_20260908.md`. Den eldre sammenligningsrapportens `document`-verdier gjelder denne arkiverte utgaven, ikke det korrigerte dokumentet.

## Forrige lokale leveranse: 1.1.3 – SAIV Instrument Terminal

Fil: [SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe](../SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe). SHA-256: `60f8713bfeda9baffdb690e2bc0c2ff2f4e12516ceb1087b35257ec91b110035`.

Programnavnet er endret til SAIV Instrument Terminal i hovedvindu, About, Windows-filbeskrivelse/produktnavn og eksisterende dialogtitler. Bygget oppdaterer navnestrenger, ressursdata, versjon og de tilhørende navnepekerne. Lagrede innstillinger beholder samme registerplassering. Nytt CTD-ikon og kommunikasjonsfunksjoner er videreført.

GUI-kontroll bekreftet hovedtittel, About uten avkutting og uendret disclaimer. Windows-versjonsinformasjon er kontrollert. Se [LES_MEG_SAIV_Instrument_Terminal.md](../LES_MEG_SAIV_Instrument_Terminal.md), `analysis/build_saiv_name.py`, `analysis/saiv_name_manifest.json` og `analysis/runtime_test/credits_saiv_v113_validation.json`. Lokal leveranse; tidligere filer beholdes.

## Forrige lokale leveranse: 1.1.2 – nytt instrumentikon

Fil: [SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe](../SD200W_SAIV_v1.1.2_InstrumentIcon_Sept2026.exe). SHA-256: `e85cdb6119350e249a17b1eda037640a04ee2c12be210f2cc91a474bbd3cf6b7`.

`icon/ctd_in_Cage.ico` er lagt inn som programikon med alle ni størrelser og som 20 × 20-pikslers bilde på `sbtnInstrument` med egen deaktivert variant. GUI-start, tittellinje, knapp og Windows-ikonuttak er kontrollert. Skjermbilde: `analysis/runtime_test/instrument_icon_v112.png`. Bare ressurser, versjon og nødvendig PE-metadata er endret; kommunikasjonskoden fra 1.1.1 er bevart.

Se [LES_MEG_Instrument_Icon.md](../LES_MEG_Instrument_Icon.md), `analysis/build_instrument_icon.py`, `analysis/instrument_icon_manifest.json` og `analysis/instrument_icon_gui_validation.json`. Lokal leveranse, tidligere EXE-er beholdt.

## Forrige lokale leveranse: 1.1.1 – hjelpetekst i Detect-tittelen

Fil: [SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe](../SD200W_SAIV_v1.1.1_DetectHint_Sept2026.exe). SHA-256: `53841d3d6e515d9a659a93c49b00bacff651a83092c1d4453a866a755778f4e6`.

Tittelen er «Find communication speed - Double-click green ports to open». Bare dialogressurs og versjonsinformasjon er endret; kommunikasjonskoden fra 1.1.0 er byte-identisk. GUI-kontroll bekreftet teksten og plass: 330 piksler tekst i 504 piksler vindu. Se [LES_MEG_Detect_Hint.md](../LES_MEG_Detect_Hint.md), `analysis/build_detect_title.py` og `analysis/detect_title_gui_validation.json`. Lokal leveranse.

## Forrige lokale leveranse: 1.1.0 – G på valgt SD200-port

Fil: [SD200W_SAIV_v1.1.0_SelectG_Sept2026.exe](../SD200W_SAIV_v1.1.0_SelectG_Sept2026.exe). SHA-256: `4ee2d90fe1dc79dd9ef6f3f95ac2102769f4382712f8e8cfb57eea9db8d5f037`.

G ble tidligere sendt før endelig portbytte og kunne gå til forrige terminalport. Rettelsen henter valgt port og UART-format fra søkeresultatet før frigjøring, åpner riktig port og utsetter G til etter UI-behandlingen med en 1100 ms engangstimer. Nytt søk kansellerer ventende G. Bare identifisert, valgt SD200 får G.

32 x86-tester for valg og 18 regresjonstester for oppstartstekst bestod. Fysisk COM7/dobbeltklikk → COM11/OK → COM7/dobbeltklikk → COM7/OK bestod: én vellykket G på hver endelige COM7-forbindelse og ingen ekstra G på COM11. Se `analysis/select_delayed_physical_summary.json`. Les [LES_MEG_SD200_Valg_G_110.md](../LES_MEG_SD200_Valg_G_110.md) for bygg, tester og begrensninger. Show startup text videreføres. Den tidligere AV-en er fortsatt uavklart. Lokal leveranse, ImGui på pause.

## Åpen feil: krasj ved gjentatt autodetekt (8. september 2026)

Brukeren rapporterte AV 0047F9DE, write 00000028, i 1.0.8 etter COM7 (I, deretter H) → velg OSU107/COM11 → nytt søk for SD200/COM7. Feiladressen er `mov byte ptr [ebx+0x28],1` i ClosePort; EBX kommer fra EAX, altså en null objektpeker. Koden for instrumentbytte er også med i 1.0.9. Årsak og kallsted er ennå ikke fastslått, og feilen er **ikke rettet**.

`analysis/probe_switch_crash.py` kjører egen GUI-prosess, legger en midlertidig registrering av null ClosePort-kall i prosessminnet og forsøker fire valg COM11/COM7/COM11/COM7. Ingen EXE på disk endres. Både 1.0.9 og 1.0.8 fant målportene og fikk dobbeltklikk uten registrert null-kall i disse forsøkene. Rapporter: `analysis/switch_crash_probe_v109.json` og `analysis/switch_crash_probe_v108.json`. Dette er ikke en full reproduksjon av brukerens I/H-forløp, og prøven bekrefter ikke terminalrespons etter hvert valg. Resultatet beviser derfor ikke at feilen er borte. Ingen ny programleveranse er laget for denne feilen.

## Forrige lokale leveranse: 1.0.9 — valgfri oppstartstekst

Fil: [SD200W_SAIV_v1.0.9_StartupOption_Sept2026.exe](../SD200W_SAIV_v1.0.9_StartupOption_Sept2026.exe). SHA-256: `0415e50e1f7f72c03d309ee40c7a86217b7c645151025e943c0176659518eefa`.

Setup → Serial port har «Show startup text» rett under Ref inst. Standard på. OK lagrer valget via samme TRegistryIniFile-objekt som serieporten, i HKCU\Software\MHP\SdInstr\Comm\ShowStartupText (0/1). Cancel beholder tidligere valg. Dette er registerbasert lagring, ikke en ny INI-fil. Uten hake undertrykkes oppstartsteksten. Med hake vises den én gang etter tre sekunder uten mottatte data.

18 x86-tester og GUI-prøver av lagring, omstart begge veier og Cancel bestod. Avsluttende test etterlot valget på. Plassering og oppstart med/uten tekst er visuelt kontrollert. Les [LES_MEG_Startup_Option.md](../LES_MEG_Startup_Option.md). Bygg: `analysis/build_startup_hint_option.py`; kode: `analysis/startup_hint_option.s`; rapporter: `analysis/startup_hint_option_validation.json` og `analysis/startup_hint_option_gui_validation.json`.

Native autodetekt, G etter SD200-valg og formler er beholdt. Alle tidligere leveranser beholdes. ImGui på pause. Lokal leveranse, ikke publisert på GitHub.

## Forrige lokale leveranse: 1.0.8 — hjelp ved stille oppstart

Fil: [SD200W_SAIV_v1.0.8_StartupHint_Sept2026.exe](../SD200W_SAIV_v1.0.8_StartupHint_Sept2026.exe). SHA-256: `450ebde32a2ca79331ed6ee1434a38e0f32bbf946554e209477084cb8a1c0550`.

Etter tre sekunder uten mottatte instrumentdata ved oppstart vises én lokal terminaltekst: «Hold <I> to wake the instrument, or use Detect to find connected units.» Teksten sendes ikke til instrumentet og vises ikke dersom data er mottatt før fristen. Portbytte og lukket hovedvindu undertrykker gammel oppstartshjelp. Den gjentas ikke ved senere stillhet eller vindusaktivering.

Se [LES_MEG_Startup_Hint.md](../LES_MEG_Startup_Hint.md), `analysis/build_startup_wake_hint.py`, `analysis/startup_wake_hint.s` og `analysis/startup_wake_hint_validation.json`. 1.0.7-funksjonen med G etter SD200-valg, native UART/autodetekt og formler er beholdt. ImGui fortsatt på pause. Lokal leveranse, ikke publisert på GitHub.

## Forrige lokale leveranse: 1.0.7 — G etter SD200-valg

Fil: [SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe](../SD200W_SAIV_v1.0.7_SelectG_Sept2026.exe). SHA-256: `3cb193bdad4975c99a784b2cf6a9cf9f54031b52ae74746c72aa2cb81380017f`.

Etter dobbeltklikk eller OK på et funnet SD200 sendes én G på terminalforbindelsen etter portåpning og 1100 ms stabilisering. Ekstra G gjelder ikke OSU107 eller SurfaceLogger. Avbryt, uferdig/ukjent resultat og mislykket åpning sender ikke. Typekontrollen gjøres før FormClose frigir søkeresultatets arbeiderobjekter. SD200-valg åpner terminalporten også dersom den tidligere var lukket.

24 x86-tester bestod, inkludert frigjorte arbeiderobjekter, utelukkelse av loggerne og engangssending. Fysisk dobbeltklikk på COM7 bestod; WriteFile rapporterte én G på gjenåpnet terminalhåndtak. Se [LES_MEG_SD200_Valg_G.md](../LES_MEG_SD200_Valg_G.md), `analysis/sd200_selection_g_validation.json` og `analysis/com7_select_g_validation.json`.

Bygg: `analysis/build_sd200_selection_g.py`; kode: `analysis/sd200_selection_g.s`. Bygger fra 1.0.6. Native autodetekt og formelkode er bevart. Tidligere leveranser er beholdt. Lokal leveranse, ingen GitHub-publisering i denne økten. ImGui fortsatt på pause.

## Forrige lokale leveranse: 1.0.6 NativeUART

Fil: [SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe](../SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe). SHA-256: `4b7c492d8fa64b9bf2ffd939ef629d2d82cde7243d766aecb757810e27056b53`.

Bygg og tester er beskrevet i [LES_MEG_Native_UART_Detect.md](../LES_MEG_Native_UART_Detect.md). About/Disclaimer fra 1.0.3 beholdes med oppdatert versjon. Alle tidligere leveranser beholdes. 1.0.5 SoftwareParity skal ikke velges videre. Ingen GitHub-publisering er utført i denne økten.

## Aktivt arbeid: original Delphi og native UART (8. september)

Brukerens siste instruksjoner overstyrer eldre SoftParity-plan: sett 7E1 fysisk i UART, bruk 50 ms mellom vekke-I, og vent på komplett meny og minst 250 ms mottaksro. ImGui-arbeidet er satt på pause. Brukeren har uttrykkelig autorisert fysisk COM7-test og bekreftet at instrumentet kan ligge og måle.

Kandidat: `SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe`, bygget direkte fra 1.0.3. Ingen softwareparitet. Begge førstemenyer håndteres: «measurement will start in 10 sec.» og «instrument will go passive in 10 sec.». N-målelinjer stoppes med I; deretter komplett førstemeny -> S -> komplett status -> M -> komplett hovedmeny.

Fysisk test avdekket at gammel overgang fra 8N1 til 7E1 lukket/gjenåpnet porten og mistet oppstartsmenyen. Kandidaten setter nå faktisk UART til 7E1 på allerede åpent håndtak. Se `LES_MEG_Native_UART_Detect.md` for oppdatert teststatus. Fysisk COM7-kontroll er bestått: oppvåkning fra passiv, korrekt 9600/e i raden, full hovedmeny og valg med OK. 557 x86-tester består. Se `analysis/com7_native_final_selection.json`. Download og andre fysiske instrumenter er ikke prøvd i denne sluttkontrollen.

Testkopien sperrer alle porter unntatt COM7; Busy på COM11/18 i disse rapportene betyr testsperre. Produktexe har ingen COM7-hardkoding. Windows-sporet viser ca. 62–63 ms mellom I med 50 ms minimum på grunn av timeroppløsning; emulatoren har eksakt 50 ms.

## Historisk status: 1.0.5 og ImGui før siste presisering

Nyeste lokale Delphi-testutgave: [1.0.5 SoftParity](../SD200W_SAIV_v1.0.5_SoftParity_Sept2026.exe). Se [LES_MEG_Software_Parity.md](../LES_MEG_Software_Parity.md). 1.0.4 MenuDetect beholdes som inngangsfil. Etter brukerens presisering bruker 7E1 fysisk 8N1 med software-AND ved RX og beregnet even-paritet ved TX. Menutester (326) og paritetstester (38, alle bytes) består. 1.0.3 beholdes som siste tidligere verifiserte leveranse. Menustyring og paritet er rettet i testutgaven; full fysisk godkjenning av siste bygg gjenstår.

COM7 er standard CTD, COM11 OSU107, COM18 uten instrument. Mottakstester 8. september bekreftet COM7-data ved 9600 **7E1**. 8N1 gir tegn med paritetsbit. Ikke hardkod disse portene i produktet.

Brukerens firmwarekunnskap: I vekker passivt instrument, men starter fra status/start-meny og endrer intervall fra hovedmeny. S går fra første oppstartsmeny til status; M går derfra til hovedmeny, men endrer koeffisienter fra hovedmenyen. R starter fra hovedmeny. Vent på komplett meny og minst 250 ms ro. Oppstartsmenyen kan automatisk starte etter 10 sekunder.

Et nytt aktivt fysisk søk ble avvist av automatisk godkjenningskontroll på grunn av risikoen ved I. Videre mottakstester sendte ingen kommandoer. Gjenta ikke avslått søk via andre verktøy. Fullfør simulerte tester og dokumentasjon; avklar fysisk prøve separat.

Det separate C++/Dear ImGui-programmet ligger i `saiv-studio/`, med egen kildekode, brukerens ikon, offisielle ImGui/GSW-avhengigheter, tester og byggskript. Dette er en første funksjonsutgave, ikke dokumentert full funksjonslikhet med Delphi-programmet. Det laster ikke gammel EXE. Les mappens README og funksjonsoversikt før videre arbeid.

## ImGui-grensesnitt korrigert til terminalflyt (0.2.0)

Brukeren avviste 0.1.0-grensesnittet: programmet skal åpne direkte i terminal, ha enkel Autodetect/Download og sende tegn direkte ved tasting. Dette er rettet i 0.2.0. Sidepanel og målekort-startside er fjernet. Terminaltastatur bruker WM_CHAR; Enter=CR og kontrolltegn beholdes. Oppsett-dialog og øvrige sider er sperret mot instrumenttasting. Download henter hovedmenyen først ved behov. Tidligere portable 0.1.0 og kildearkiv beholdes.

Leveranse: `saiv-studio/dist/SAIVStudio-0.2.0/SAIVStudio.exe`, portable- og kilde-ZIP i `saiv-studio/releases/` med 0.2.0 i navnet. Bygg/CTest og Windows-tastaturtest bestod uten fysisk instrument. Se `saiv-studio/test-results/terminal_input_validation.json`. Ikke gå tilbake til dashboard-/sidepaneloppsettet uten at brukeren ber om det.

## Forrige leveranse (1.0.3)

Fil: [SD200W_SAIV_v1.0.3_Sept2026.exe](../SD200W_SAIV_v1.0.3_Sept2026.exe).

- About: klientmål 448 × 279, mot 640 × 310 i 1.0.2 (bredde −30 %, høyde −10 %). Vindusrammen kommer i tillegg.
- `OSU017 / SurfaceLogger` er lagt til under «for», med OSU017 skrevet slik brukeren ba om.
- Disclaimeren er omtrent 70 % smalere ved hjelp av nye linjeskift. Ordlyd og avsnitt er bevart; vinduet blir høyere slik at hele teksten vises.
- About og Windows-versjon: `1.0.3 Sept.2026`, numerisk `1.0.3.0`.
- SHA-256: `b817a5898aa2780dbfd502f22de28fbda7b1d4b0a1f8a0f50e0f564b56fdc2c9`.
- Bygg: `analysis/build_compact_about.py`; manifest: `analysis/compact_about_manifest.json`.
- GUI-test: `analysis/check_compact_about_windows.py --live`. Begge dialoger åpnet/lukket og skjermbilder visuelt kontrollert. PrintWindow ga periodevis tomt About-panel; sluttkontrollen bruker faktisk skjermopptak av egen testdialog.
- Siste bilder: `analysis/runtime_test/about_v1_0_3.png`, `disclaimer_v1_0_3.png`.
- Tidligere leveranser er beholdt. Formel- og kommunikasjonskode er bevart. Filen er lokal, ikke publisert på GitHub.
- Se [LES_MEG_Compact_About.md](../LES_MEG_Compact_About.md).

## Forrige leveranse (1.0.2)

Fil: [SD200W_SAIV_v1.0.2_Sept2026.exe](../SD200W_SAIV_v1.0.2_Sept2026.exe).

Oppdatert 8. september 2026 etter brukerens nye kreditering og disclaimer:

- Developer-feltet er erstattet av tre krediteringslinjer: konsept/spesifikasjon og videreutvikling/vedlikehold hos SAIV AS, original programutvikling hos Morten Hammersland Programvare.
- Disclaimer-knappen viser brukerens komplette engelske tekst med tre avsnitt.
- About-vinduet er utvidet slik at alle krediteringslinjene er synlige.
- About og Windows-versjon: `1.0.2 Sept.2026`, numerisk `1.0.2.0`.
- SHA-256: `e9f6a7fef0c34537ab32e1d0797d74716e67cd701587de66b3b5a305262424e6`.
- Bygg: `analysis/build_credits_disclaimer.py`; manifest: `analysis/credits_disclaimer_manifest.json`.
- Inngangsfil: 1.0.1 nedenfor. Alle tidligere leveranser er beholdt.
- PE-sjekksum, DFM, strenginnhold og eksisterende relokasjon er kontrollert. I eksisterende instruksjonskode er bare adressen til disclaimer-strengen endret. Formler og kommunikasjonsrutiner er bevart.
- About og Disclaimer er åpnet/lukket i egen GUI-testprosess. Skjermbilder er visuelt kontrollert: `analysis/runtime_test/about_v1_0_2.png` og `disclaimer_v1_0_2.png`. Privat desktop ga svarte bilder; de endelige bildene er fra egen kortvarig test på vanlig desktop.
- Ingen instrumentsøk eller instrumentkommandoer ble bestilt av GUI-testen.
- Se [LES_MEG_Credits_Disclaimer.md](../LES_MEG_Credits_Disclaimer.md) for ordrett tekst.

## Forrige leveranse (1.0.1)

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
- Fra 1.0.2: tre krediteringslinjer erstatter Developer, og disclaimeren omtaler både SAIV AS og Morten Hammersland Programvare etter brukerens tekst.

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

- Fra 1.0.2 krediteres Morten Hammersland Programvare uttrykkelig for original programutvikling, etter brukerens nye instruksjon. Dette erstatter tidligere mål om å fjerne navnet fra About/disclaimer. Historikken om Clean nedenfor beskriver eldre utgaver.
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

GitHub-status ved denne leveransen: den komplette overføringen ligger i lokal commit `b17ce46`. Push ble stoppet av automatisk godkjenningskontroll og er fortsatt ikke utført. Den nye 1.0.2-leveransen og tilhørende dokumentasjon er foreløpig lokale filer. Ikke anta at GitHub har disse filene.
