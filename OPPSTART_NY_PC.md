# Videre arbeid med SD200W på en ny PC

## Hent hele prosjektet

Bruk Windows og Git. Kjør i PowerShell fra mappen du vil ha prosjektet i:

```powershell
git clone https://github.com/BaardSagen/SD200w_R2.git
cd SD200w_R2
```

Alternativt: GitHub → Code → Download ZIP, pakk ut hele arkivet og åpne PowerShell i rotmappen. Ikke hent bare siste EXE dersom du skal videreutvikle programmet. Prosjektet trenger ikke ligge i `C:\cprojects\delphi`.

Les først [PROSJEKTSTATUS](sd200DOc/PROSJEKTSTATUS.md), deretter [FORMELKARTLEGGING](sd200DOc/FORMELKARTLEGGING.md), [FORMELKONTROLL](sd200DOc/FORMELKONTROLL.md) og relevante `LES_MEG_*.md`. `AGENTS.md` gir også neste kodeassistent disse føringene.

## Kjøre programmet

Start `SD200W_SAIV_v1.0.1_Sept2026.exe`. Python og assembler trengs bare for analyse/bygg/test. Installer instrumentets USB-/serieportdriver dersom Windows ikke oppretter COM-porten. Bruk Detect til å finne dagens portnummer; COM7 og COM11 i historiske notater er bare tidligere oppkobling. Lokale INI-innstillinger følger ikke med.

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

Siste versjonsbygg trenger bare Python-avhengighetene:

```powershell
.\.venv\Scripts\python.exe analysis/build_version_1_0_1.py
.\.venv\Scripts\python.exe analysis/verify_transfer.py
```

Dette gjenskaper 1.0.1 fra den medfølgende `SD200W_SAIV_OSU107_NoHandshake.exe`. For nye endringer bruker du siste leveranse som referanse og lager ny utdatafil.

Bygg som assemblerer `.s` trenger GNU Binutils med `as --32`, `objcopy`, `objdump` og `nm` i PATH. Det opprinnelige miljøet brukte MinGW Binutils 2.28. Kontroller `as --version` og `Get-Command as,objcopy,objdump,nm` før slike bygg. `.o` og `.bin` gjenskapes av byggskriptene og er ikke med i Git.

## Hva følger med, og hva er separat?

Alle `LES_MEG`-notater, prosjekt-/formeldokumenter, analyseskript, assemblerkilder, manifester, disassemblering, testresultater og historiske EXE-er følger med. `analysis/transfer_inventory.json` er den konkrete fillisten for denne overføringen.

`analysis/runtime_test/` inneholder historiske testbevis, inkludert mislykkede forsøk. At en fil ligger der betyr ikke at forsøket bestod. Les prosjektstatus for vurderingene.

`docs/` og `osu107Doc/` er referansedokumentasjon fra separate firmware-/instrumentprosjekter. Henvisninger der til for eksempel `sd208_a2/`, Keil, firmwarekildekode og andre arbeidsmapper betyr ikke at disse separate prosjektene følger med. Alt som finnes av disse dokumentene i denne SD200W-arbeidsmappen er inkludert.

Avhengighetsmapper, Python-cache, editorinnstillinger, lokale INI-filer og regenererbare assemblerobjekter er utelatt. Tidligere lokale Git-grener er bevart lokalt; filene leveres samlet på `main`.

Fysiske instrumenttester må tilpasses dagens porter og instrumenttilstand. Les skriptet før kjøring: wake-/Download-/Detect-tester kan sende kommandoer og endre instrumentets tilstand. Automatisk testoppdagelse av alle `check_*.py` er ikke en trygg oppstartsprosedyre.

## Kontrollert overføring

Se [OVERFORINGSKONTROLL.md](sd200DOc/OVERFORINGSKONTROLL.md) for resultatene fra rent Python-miljø, separat prosjektkopi og gjenskaping av siste EXE.
