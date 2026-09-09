# LES MEG – fysisk 8N1 med programvareparitet

Lokal Delphi-testutgave: **SD200W_SAIV_v1.0.5_SoftParity_Sept2026.exe**. Dato: 8. september 2026.
SHA-256: `83c1637f51d8c1fe385e8ad00a26fe5021df2156a5168932f56799a4c0c9bdd1`.

Bygger videre på 1.0.4 MenuDetect. Alle tidligere utgaver er beholdt. Utgaven er lokal og ikke lagt på GitHub.

## Slik virker det

For instrumenter med logisk **7E1** settes Windows-porten fysisk til **8N1**. Ved mottak fjernes bit 7 med AND 0x7F. Ved sending settes bit 7 slik at antallet enere i hele byten blir partall. Eksempel: I (0x49) sendes som 0xC9. G, S og M får henholdsvis 0x47, 0x53 og 0x4D. Baudrate må fortsatt være lik på begge sider. Det foretas ikke kontroll av mottatt paritet.

Vanlig 8N1, blant annet OSU107, sendes og mottas uten byteendring. E/7 i programmets eksisterende innstillinger beskriver den **logiske** instrumentprotokollen; selve driveren bruker 8N1. Andre eldre kombinasjoner utenfor 7E1/8N1 er ikke konvertert av denne patchen.

Dette ligger i felles seriekommunikasjon, ikke bare Detect. Patchen gjelder de eksisterende SetCommState-kallene, seriell ReadFile og UniqueString-kallet foran seriell WriteFile. Den siste lager en privat streng før kodingen; konstante/delte kommandostrenger endres ikke. Filer og loggerens binærdata i vanlig 8N1 blir ikke maskert.

Detect beholder menuflyten fra [LES_MEG_Menu_Detect.md](LES_MEG_Menu_Detect.md), inkludert 250 ms ro og riktig S/M-tilstand. De to logiske formatene prøves fortsatt separat, men begge går fysisk gjennom 8N1. En høy bit alene er ikke positiv instrumentidentifikasjon.

## Kontroller

- Menusøk: 326 x86-scenarier, inklusive alle oppdelinger av to menyer med 400 ms pause mellom fragmentene, normal/flyttet innlasting, avbrudd og paritetsmønster. Rapport: `analysis/menu_detect_validation.json`.
- Programvareparitet: 38 x86-scenarier med alle 256 byteverdier. Testen kjører også den faktiske Delphi-rutinen for kopiering av delte strenger, tester feil/tomt mottak, stakk/registere, flyttet innlasting og bevaring av logisk DCB. Rapport: `analysis/soft_parity_validation.json`.
- Siste EXE starter i isolert GUI-instans uten feildialoger. Testen sendte ingen instrumentkommandoer.
- Faktisk COM7-mottak er bekreftet ved 9600: 8N1 viser paritetskodede N-rader, 7E1 viser de samme datatypene lesbart. Se mottaksrapportene i `analysis`. Det bekrefter datagrunnlaget for programvaredekodingen, men er ikke en full fysisk test av siste EXE.

**Full fysisk godkjenning av siste EXE gjenstår.** Automatisk godkjenningskontroll avviste gjentatt aktivt søk fordi I kan endre instrumenttilstand. Videre fysisk kontroll var kun mottak. Ikke omgå avvisningen med et annet verktøy. Brukeren vurderer videre bruk etter samtale med Morten Hammersland.

## Videreføring på en annen PC

Les `OPPSTART_NY_PC.md`. Behold 1.0.3 og 1.0.4 som inngangsfiler og installer prosjektets Python-avhengigheter og GNU binutils. Byggtrinnene er hashbundet:

```powershell
python analysis/build_menu_detect.py
python analysis/build_soft_parity.py
python analysis/test_menu_detect.py
python analysis/test_soft_parity.py
python analysis/check_startup_windows.py SD200W_SAIV_v1.0.5_SoftParity_Sept2026.exe --look-only
```

Original Delphi-kilde finnes fortsatt ikke i prosjektet. Dette er en dokumentert EXE-patch. Kreditering, disclaimer, kompakte dialoger og eksisterende formler er bevart; versjonen er oppdatert til 1.0.5.

Det separate ImGui-programmet har samme programvareparitet i ny C++-kode. Se `saiv-studio/README.md` og `saiv-studio/docs/KOMMUNIKASJON.md`.
