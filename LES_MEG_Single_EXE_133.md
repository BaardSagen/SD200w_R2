# SAIV Instrument Terminal 1.3.3 - en EXE til kunden

Leveranse 9. september 2026: **SAIV_Instrument_Terminal_v1.3.3_Sept2026.exe**.

Kunden kopierer og starter bare denne ene filen. Ingen separat DLL, ZIP-utpakking eller installasjonsprogram trengs.

## Automatisk oppsett

Ved forste oppstart legger EXE-filen innebygd program og Convert/Merge-modul i **%LOCALAPPDATA%\SAIV_IT\1.3.3_23c455263801**. Filene heter SAIV_IT_Runtime.exe og SIT_Import131.dll. Disse blir liggende. Ved senere start kontrolleres hele filinnholdet mot de innebygde kopiene. Intakte filer gjenbrukes uten omskriving, mens manglende eller skadede filer gjenopprettes automatisk. Hver utgave har egen innholdsmerket mappe.

Programmet skriver ikke disse filene ved kundens EXE. EXE-filen kan flyttes eller gis nytt navn. Samtidige oppstarter samordner klargjoringen og kan bruke de samme intakte filene. Kundens arbeidsmappe og kommandolinjeargumenter viderefores til Delphi-programmet.

## Rettigheter og administrerte PC-er

Dette krever **ikke administratorrettigheter**. Oppstarteren er eksplisitt merket asInvoker og bruker brukerens egen AppData. Windows-testen bekrefter at bade oppstarter og runtime har TokenElevation=0, og at gjenoppretting fungerer uten elevasjon.

Universiteters egne AppLocker/WDAC-regler eller andre IT-regler kan likevel blokkere et ukjent program eller kjoring fra AppData. Det ma eventuelt godkjennes av institusjonens IT-avdeling. Denne leveransen endrer ikke slike regler. Et lokalt mappevalg er ikke nodvendig for a unnga admin og er ikke lagt til. Signering er fortsatt utsatt etter tidligere avtale.

## Kontroller

- Start fra mappe som bare inneholder den leverte EXE-en, og fra flyttet/omdopt EXE med mellomrom og norske tegn i mappebanen.
- Faktisk Merge-dialog, skanning ved 0/0.5/10 s, to tilleggsfiler, dato/tid-valg, eksport med/uten skillekolonne, header og overskrivingsvern.
- 4108 eksportverdier sammenlignet med uavhengig fasit.
- Convert fra innebygd DLL apner feltveiviseren for faktisk OSU-fil.
- Neste oppstart gjenbruker intakte filer uten omskriving.
- Slettet DLL, skadet DLL og slettet runtime gjenopprettes byte-identisk.
- To samtidige oppstarter deler filene. Oppstarter og runtime kjorte uten administratorrettigheter.

Rapporter: analysis/runtime_test/single133/gui_validation.json, gui_numeric_validation.json og cache_validation.json. De eldre COM-porttestene gjelder fortsatt: innebygd runtime er identisk med 1.3.2 bortsett fra About/Windows-versjon og PE-sjekksum. Convert/Merge-DLL er byte-identisk med 1.3.1; eksportheader viser fortsatt denne modulversjonen. Ingen ny fysisk instrumenttest.

## Bygg og videre arbeid

Bygg: **python analysis/build_single_exe_133.py**. Kilde: sit_single/launcher.cpp og launcher.manifest. bundle_config.h genereres av bygget. Avhengigheter: bevart 1.3.2-EXE, SIT_Import131.dll, instrumentikon, Python/pefile og MinGW g++/windres. Kunden trenger bare Windows.

Oppstarteren inneholder to RCDATA-ressurser og bruker Windows CreateProcess med konkret programbane. Det kjores en oppstarterprosess og en Delphi-prosess. Ingen nedlasting eller nettforbindelse er nodvendig. Eksisterende brukerinnstillinger, siste COM-port og kommunikasjon er beholdt. Tidligere leveranser er bevart. Ingen GitHub-push.

Microsoft-referanse for asInvoker: https://learn.microsoft.com/en-us/windows/win32/secbp/running-with-administrator-privileges
