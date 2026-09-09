# Videre arbeid med SD200W på en ny PC

## Lokal status 8. september 2026

Komplett GitHub-push er fortsatt ikke utført. GitHub alene inneholder ikke alt som beskrives her. Kopier hele den lokale prosjektleveransen, eller vent på godkjent publisering. Ny Delphi-leveranse: `SAIV_Instrument_Terminal_v1.3.0_Sept2026.exe`; les `LES_MEG_SAIV_Instrument_Terminal.md`, `LES_MEG_Instrument_Icon.md`, `LES_MEG_Detect_Hint.md`, `LES_MEG_SD200_Valg_G_110.md`, `LES_MEG_Startup_Option.md` for fysisk teststatus. ImGui-arbeidet er satt på pause. Det tidligere komplette prosjektarkivet er et historisk øyeblikksbilde og inneholder ikke automatisk denne senere kandidaten.

Det nye ImGui-programmet har egen portabel ZIP og komplett kilde-ZIP i `saiv-studio/releases/`. Kilde-ZIP-en inkluderer vendorkilde og lisenser; den er pakket ut i en ny mappe og bygget/testet uten original Delphi-EXE. Se `analysis/studio_transfer_validation.json` og `saiv-studio/README.md`. De lokale vendor-mappene har egne Git-metadata; ved senere Git-publisering må avhengighetene tas med eksplisitt eller via den komplette kilde-ZIP-en, ikke som utilsiktede tomme gitlinks.

## Hent hele prosjektet

Bruk Windows og Git. Kjør i PowerShell fra mappen du vil ha prosjektet i:

```powershell
git clone https://github.com/BaardSagen/SD200w_R2.git
cd SD200w_R2
```

Alternativt: GitHub → Code → Download ZIP, pakk ut hele arkivet og åpne PowerShell i rotmappen. Ikke hent bare siste EXE dersom du skal videreutvikle programmet. Prosjektet trenger ikke ligge i `C:\cprojects\delphi`.

Les først [PROSJEKTSTATUS](sd200DOc/PROSJEKTSTATUS.md), deretter [FORMELKARTLEGGING](sd200DOc/FORMELKARTLEGGING.md), [FORMELKONTROLL](sd200DOc/FORMELKONTROLL.md) og relevante `LES_MEG_*.md`. `AGENTS.md` gir også neste kodeassistent disse føringene.

## Kjøre programmet

Siste lokale leveranse er `SAIV_Instrument_Terminal_v1.3.0_Sept2026.exe`. Denne utgaven bruker faktisk UART-paritet; gjeldende tester er dokumentert i `LES_MEG_Native_UART_Detect.md`. 1.0.5 skal ikke velges videre. Python og assembler trengs bare for analyse/bygg/test. Installer instrumentets USB-/serieportdriver dersom Windows ikke oppretter COM-porten. Bruk Detect til å finne dagens portnummer; COM7 og COM11 i historiske notater er bare tidligere oppkobling. Lokale brukerinnstillinger i Windows-registeret følger ikke automatisk med prosjektfilene. «Show startup text» er på som standard på en ny PC.

## Sette opp analyse og tester

Det eksisterende miljøet bruker Python 3.11.3, 64-bit. Installer Python 3.11 x64 med Python Launcher, og kjør følgende fra prosjektets rotmappe:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe analysis/verify_transfer.py
.\.venv\Scripts\python.exe analysis/test_recovered_formulas.py
.\.venv\Scripts\python.exe analysis/audit_formulas.py
.\.venv\Scripts\python.exe analysis/test_no_handshake.py
```

Ingen aktivering av PowerShell-skript er nødvendig. Pakkeinstallasjonen trenger nettilgang. `analysis/python_packages` er en lokal avhengighetsmappe fra den gamle PC-en og er ikke nødvendig etter installasjon i `.venv`.

`verify_transfer.py` kontrollerer at de overførte prosjektfilene finnes og at alle EXE-filer har riktig SHA-256. Formeltesten har 24 sammenligninger mot emulert maskinkode. Audit-skriptet skriver referanse-/grensetilfeller til JSON; det er en analyserapport, ikke en fullstendig automatisk faglig godkjenning. Disse testene bruker emulator og sender ikke instrumentkommandoer. Rapportene skrives til `analysis/`.

Flere tester uten fysisk instrument:

```powershell
.\.venv\Scripts\python.exe analysis/test_guard.py
.\.venv\Scripts\python.exe analysis/test_refresh.py
.\.venv\Scripts\python.exe analysis/test_logger_clean.py
.\.venv\Scripts\python.exe analysis/test_refresh_reply.py
```

## Bygg og patching

Vi har ikke original Delphi-kildekode. Byggskriptene endrer bestemte eksisterende EXE-filer og sjekker ofte kildehash. Originalen og tidligere programutgaver følger derfor med under sine opprinnelige navn i rotmappen.

Kjør bygg i en separat klone/kopi: skriptene skriver over sine navngitte utdatafiler. Kontroller inngangsfil og forventet hash før hvert trinn. Ikke kjør alle byggskript alfabetisk. Ikke alle historiske varianter har et eget komplett byggskript.

Historisk versjonsbygg for 1.0.1 trenger bare Python-avhengighetene:

```powershell
.\.venv\Scripts\python.exe analysis/build_version_1_0_1.py
.\.venv\Scripts\python.exe analysis/verify_transfer.py
```

Dette gjenskaper 1.0.1 fra den medfølgende `SD200W_SAIV_OSU107_NoHandshake.exe`. For nye endringer bruker du siste leveranse som referanse og lager ny utdatafil.

Bygg som assemblerer `.s` trenger GNU Binutils med `as --32`, `objcopy`, `objdump` og `nm` i PATH. Det opprinnelige miljøet brukte MinGW Binutils 2.28. Kontroller `as --version` og `Get-Command as,objcopy,objdump,nm` før slike bygg. `.o` og `.bin` gjenskapes av byggskriptene og er ikke med i Git.

Forrige 1.1.0 bygges fra den bevarte 1.0.9 med GNU Binutils og Python:

```powershell
python analysis/build_sd200_selection_g_delayed.py
python analysis/test_sd200_selection_g_delayed.py
python analysis/test_startup_hint_option_v110.py
python analysis/verify_transfer.py
```

Les `LES_MEG_SD200_Valg_G_110.md` før eventuelle fysiske COM-porttester.

## Hva følger med, og hva er separat?

Alle `LES_MEG`-notater, prosjekt-/formeldokumenter, analyseskript, assemblerkilder, manifester, disassemblering, testresultater og historiske EXE-er følger med. `analysis/transfer_inventory.json` er den konkrete fillisten for denne overføringen.

`analysis/runtime_test/` inneholder historiske testbevis, inkludert mislykkede forsøk. At en fil ligger der betyr ikke at forsøket bestod. Les prosjektstatus for vurderingene.

`docs/` og `osu107Doc/` er referansedokumentasjon fra separate firmware-/instrumentprosjekter. Henvisninger der til for eksempel `sd208_a2/`, Keil, firmwarekildekode og andre arbeidsmapper betyr ikke at disse separate prosjektene følger med. Alt som finnes av disse dokumentene i denne SD200W-arbeidsmappen er inkludert.

Avhengighetsmapper, Python-cache, editorinnstillinger, lokale INI-filer og regenererbare assemblerobjekter er utelatt. Tidligere lokale Git-grener er bevart lokalt; filene leveres samlet på `main`.

Fysiske instrumenttester må tilpasses dagens porter og instrumenttilstand. Les skriptet før kjøring: wake-/Download-/Detect-tester kan sende kommandoer og endre instrumentets tilstand. Automatisk testoppdagelse av alle `check_*.py` er ikke en trygg oppstartsprosedyre.

## Kontrollert overføring

Se [OVERFORINGSKONTROLL.md](sd200DOc/OVERFORINGSKONTROLL.md) for resultatene fra rent Python-miljø, separat prosjektkopi og gjenskaping av siste EXE.

Forrige 1.1.1 bygges fra bevart 1.1.0 med `python analysis/build_detect_title.py`. Bare Python/pefile kreves for dette ressurstrinnet.

Forrige 1.1.2 bygges fra bevart 1.1.1 og `icon/ctd_in_Cage.ico` med `python analysis/build_instrument_icon.py`. Python-avhengigheter: pefile og Pillow.

Nyeste SAIV Instrument Terminal 1.1.3 bygges fra bevart 1.1.2 med `python analysis/build_saiv_name.py` (Python/pefile). Registerplasseringen er beholdt for eksisterende brukerinnstillinger.

Import fra 1.2.2 krever `SIT_Import130.dll` i samme mappe som EXE-filen. Les `LES_MEG_Import_122.md`. Kildekode og bygg for importmodulen ligger i `sit_import/` og `analysis/build_logger_import_130.py`; bygggrunnlag er bevart 1.1.3. Loggerdata har eget datavindu og FIELDS-eksport; gamle profil-/standarddybdeeksporter er ikke utvidet til loggergrenen ennå.

1.2.2: feltvalg med originalhake på som standard, C→S, P→Real depth med valgfri GPS-header, eksplisitt PAR-arealenhet og OX/OxR. P er dbar, AP er mbar/hPa. Dybden følger SITs Fixed position/EOS-80-gren. Se siste prosjektstatus før videre endringer.

SIT 1.3.0 har Merge med mappeskanning og 0.0–10.0 sekunders toleranse. Les LES_MEG_Merge_130.md. Testfiler: data/saiv110. Merge-kilde: sit_import/merge.h og merge_ui.inc. 1.2.2-kilden er bevart i analysis/reference/sit_import_v122. Se siste prosjektstatus for avklarte koblingsregler og tester.
