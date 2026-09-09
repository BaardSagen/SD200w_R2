# SAIV IT 1.3.9 - Interval og TIME/DATE

Kunden trenger bare SAIV_Instrument_Terminal_v1.3.9_Sept2026.exe. Innebygd runtime og SIT_Import139.dll pakkes ut automatisk uten administratorrettigheter. Tidligere EXE-er er beholdt.

## Bruk

1. Kjoer Detect (Alt+E) og godta riktig enhet og port.
2. Interval (Alt+I) setter maaleintervallet. TIME/DATE (Alt+A) setter klokke fra PC-en; velg LT (Windows lokal tid, inkludert sommertid) eller GMT (UTC).
3. Download (Alt+D), Interval og TIME/DATE er deaktivert foer bekreftet Detect og ved lukket/endret port. Ny enhet eller port krever ny Detect.

Setup er flyttet under Save text. Print staar paa den tidligere Setup-plassen. Interval og TIME/DATE ligger etter Merge. Save text beholder Alt+T. Log-knappen forblir skjult.

## Enheter

- SD200: instrumentets eget intervall og egen klokke.
- OSU107: intervallet settes i tilkoblet SD200. TIME/DATE setter og kontrollerer foerst SD200-klokken, deretter loggerklokken. Dialogen oppgir om bare foerste del ble bekreftet dersom neste del feiler.
- SAIV110 Surface: bare loggerklokken settes. Interval endrer bare [surface].intervalSeconds i config/system.ini, og sender lokal U for MIR + APPLY.

Alle enheter tilbyr samme elleve intervaller: 1, 2, 5, 10, 20 og 60 sekunder, samt 5, 10, 30, 60 og 180 minutter. Ingen fritekst for Surface.

For Surface bekreftes stopp, disken oppdateres via F/Y, og brukeren velger config/system.ini paa den tilkoblede loggerdisken. Originalfilen beholdes som system.ini.sit-backup-.... Andre innstillinger og kalibreringer beholdes byte for byte. Filen skrives og flushes; etter 10 sekunder sendes U. Bare den endelige OK SAIV110_UPDATE_CONFIG godtas som APPLY-bekreftelse. Diskverdien kontrolleres igjen og loggeren etterlates stoppet. Ved feil beholdes sikkerhetskopien; ukjent APPLY-status overskrives ikke med en automatisk gjenoppretting.

## Kommunikasjon og verifisering

Bruker terminalens eksisterende seriellforbindelse, oppdaget port/baudrate og ekte UART-paritet. Ingen parallell portleser. Kommandoer sendes etter komplette menyer/prompter og mottaksro, med tidsfrister. SD200-klokketekst sendes tegnvis med ekkokontroll og minst 60 ms mellom tegn. Logger-X sendes samlet etter formatprompten. LT/GMT endrer etiketten; riktig lokaltid eller UTC er allerede sendt.

SD200 intervall og klokke leses tilbake. Loggerklokken kontrolleres mot fersk USB-status etter kontrollert gjenapning med 750 ms mellomrom. Serienummer og loggermodus sammenlignes naar serienummer finnes i Detect-svaret. Klokkekontrollen godtar opptil fem sekunders avvik fra PC-klokken under overfoering og avlesning. SD200-avlesningen kontrolleres foer retur til den lange hovedmenyen. Hvis tegnvis overfoering gir et maalt etterslep paa mer enn 5 og hoeyest 30 sekunder, gjentas klokkeskrivingen EN gang med maalt forsinkelse lagt til PC-tiden; ny avlesning maa fortsatt bestaa samme kontroll. Sovende SD200 vekkes med avgrensede I-tegn med minst 60 ms mellomrom; sending stopper ved foerste mottak. Etter Enter kan tiden allerede vaere skrevet selv om neste bekreftelse mangler; feilvinduet opplyser om dette. PC-aar maa vaere 2000-2099, og SD200 begrenses til 2079.

Bygg: analysis/build_single_exe_139.py fra hashbundet analysis/single138/SAIV_IT_Runtime.exe. Instrumentkode: sit_import/settings_protocol.h og settings_ui.inc. Native gates og DFM-endringer: analysis/patch_settings139.py. Importkildene fra 1.3.7 er arkivert i analysis/reference/sit_import_v137, og 1.3.7-byggskriptet bruker arkivet.

Tester: protokollkontroller for alle intervaller, klokker, LT/GMT, tilbakeavlesning, Surface-stopp og bevaring av INI; register/stack/ASLR-kontroll av native gates; GUI-kontroll av alle tre enhetstyper, elleve intervaller, snarveier, plassering og deaktivering ved portbytte. Eksisterende import/grafer, Convert og gammel ASCII-import regresjonstestes. Rapporter: analysis/settings139_release_validation.json og analysis/runtime_test/settings139/startup_validation.json.

Brukeren autoriserte fysisk test paa SD200 COM7 og OSU107 med instrument COM11. COM7 er SD204, serienummer 1756: intervall 2 sekunder beholdt og klokke satt/kontrollert mot PC-GMT. Klokken viste foer testen dato 97-04-12; den er korrigert til 2026. COM11 er OSU107 SN107 med SD208 serienummer 1456: intervall 1 sekund beholdt; baade SD200- og loggerklokken satt og kontrollert mot PC-LT. Den faktiske Change GMT/LT: Y/N-varianten og lang OSU-meny/vekking er lagt inn i regresjonskontrollene. Fysisk rapport: analysis/runtime_test/settings139/physical_gui_validation.json; opprinnelige verdier: physical_preflight.json i samme mappe.

SAIV110 Surface er protokoll- og GUI-testet, men ikke fysisk testet i denne leveransen. Ingen modusendring er gjort paa OSU107 for aa teste Surface. Protokollgrunnlag: docs/intervall_sd200_saiv110.md og docs/klokkesetting_osu107_sd200_saiv110.md. Ingen firmwareendring og ingen GitHub-push.
