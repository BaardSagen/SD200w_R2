# SAIV Instrument Studio 0.2.0

Første selvstendige Windows-utgave i C++ / Dear ImGui / DirectX 11. Dette er et nytt program med egen kode. Det laster ikke Delphi-programmet. Ikonet er brukerens `icon/ctd_in_Cage.ico`.

## Start

Kjør `SAIVStudio.exe`. Programmet åpner direkte i terminalen, med **Autodetect** og **Download** øverst.

1. Trykk Autodetect, vent på søkeresultatene og velg instrumentet. Det kobles til direkte.
2. Skriv i terminalen: hvert ASCII-tegn sendes uten eget tekstfelt eller Send-knapp. Enter sender CR, Backspace sender 0x08, Delete sender 0x7F. Kontrolltegn beholdes.
3. Trykk Download for å motta data. Ved behov hentes hovedmenyen først gjennom den menybevisste flyten.

Setup åpner portinnstillinger i en egen dialog. Tegn skrevet der eller på andre programsider sendes ikke til instrumentet. Automatisk kommunikasjon og køet terminalinput respekterer 250 ms ro etter mottatt tekst. Under en pågående automatisk operasjon avvises terminalkommandoer med beskjed; bruk Cancel først.

Grafer/data, Utilities og Logger files finnes som enkle knapper øverst. Målekort-startsiden og sidepanelet er fjernet. `--demo` viser syntetiske eksempeldata uten instrument. `--terminal-test <fil>` bruker en isolert filtransport for tastaturtesting, uten COM-port.

Se [funksjonsstatus](docs/FUNKSJONSSTATUS.md), [kommunikasjon](docs/KOMMUNIKASJON.md) og [kildegrunnlag](docs/KILDEGRUNNLAG.md). Full funksjonslikhet med det gamle programmet er **ikke** ferdig. Fysisk akseptansetest gjenstår.

## Bygg og viderefør på annen PC

Kildepakken inkluderer `src`, `assets`, tester, eksempelfiler og vendorkilde. Installer Visual Studio med Desktop development with C++, Windows SDK, CMake og Ninja. Kjør `build.cmd` fra kildekatalogen. Skriptet finner Visual Studio via vswhere, bygger Release x64 med statisk C++ runtime og kjører CTest. Sluttfil: `build/SAIVStudio.exe`.

```powershell
.\build.cmd
cmake --install build --prefix dist/SAIVStudio-0.2.0
```

Ingen nettverksnedlasting er nødvendig fra komplett kildepakke. `tests/terminal_input_windows.py` krever Python og Pillow og starter en egen demo-instans. Den tester direkte WM_CHAR, kontrolltegn, fokusbeskyttelse, navigasjon og skjermbilder med faktiske museklikk. Ikke kjør den mens du bruker musen til annet arbeid. Kjerne-/protokolltester bruker ingen instrumenter.

Windows x64 og DirectX 11 kreves. Windows-fontene Segoe UI/Consolas brukes når de finnes, med fallback. Innstillinger lagres under `%LOCALAPPDATA%/SAIV/InstrumentStudio/settings.txt`. Ingen server, konto eller installasjonstjeneste brukes.

Always keep backup copies of your data files and verify measurement results before relying on them.

Se [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) og medfølgende lisenser. Denne lokale utgaven er ikke publisert til GitHub.
