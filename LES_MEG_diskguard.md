# SD200W med sperre for nedlasting i diskmodus

Start **SD200W_diskguard.exe** for å bruke den endrede versjonen. Originalfilen
**SD200W.exe** er ikke endret.

Når programmet mottar **Refresh disk Y/N** fra instrumentet, kjenner det igjen
diskmodus. Et pågående forsøk som ble startet med Download-knappen avbrytes, og
programmet viser:

> Download virker ikke i denne modusen

Download-knappen viser deretter samme melding uten å starte et nytt forsøk.
Sperren nullstilles når programmet lukker instrumentets COM-forbindelse, eller
når programmet startes på nytt. Ved bytte av instrument: koble fra og velg
COM-porten på nytt.

Gjenkjenningen tåler store/små bokstaver, mellomrom, linjeskift og tekst som
ankommer i flere deler. Loggernavnet spiller ingen rolle. Sperren sender ikke
noe Y/N-svar eller ekstra avbruddstegn til instrumentet. Log-knappen beholder
den opprinnelige behandlingen.

## Kontroll før bruk

Endringen er testet ved å emulere de endrede x86-instruksjonene med simulerte
instrumentsvar. Hele programmet og kommunikasjonen med fysisk instrument er
ikke testet. Kontroller derfor med ditt instrument at:

1. Download gir meldingen når instrumentet svarer med diskspørsmålet.
2. Programmet kan brukes videre etter at meldingen lukkes.
3. Vanlig nedlasting fortsatt fungerer med et instrument som sender målelinjer.

Den endrede kopien er usignert, siden en endring i EXE-filen ugyldiggjør den
opprinnelige digitale signaturen. Originalfilens signatur er beholdt.

## Teknisk dokumentasjon

Endringen gjelder bare den konkrete EXE-versjonen i denne mappen. Byggeskriptet
kontrollerer originalens SHA-256 og forventede instruksjoner før det lager en
kopi. Det legger til én seksjon og fire kodekoblinger. Originale ressurser og
importer er beholdt.

- `analysis/download_guard.s`: kildekoden til sperren.
- `analysis/build_guard.py`: lager `SD200W_diskguard.exe` fra originalen.
- `analysis/test_guard.py`: tester med Unicorn, uten å åpne COM-porter.
- `analysis/patch_manifest.json`: adresser, endringer og SHA-256-kontrollsummer.

Bygg: `python analysis/build_guard.py` (krever pefile og GNU as/objcopy/nm).

Test: `python analysis/test_guard.py` (Unicorn ligger i `analysis/python_packages`).
