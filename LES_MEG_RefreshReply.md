# Kontroller svaret etter Y

Program: `SD200W_SAIV_OSU107_RefreshReply.exe`.
Bygger videre på Clean-versjonen. Tidligere programfiler er beholdt.

Etter automatisk Y leser programmet svaret fra instrumentporten. Mottak og Windows-meldinger behandles mens det venter, i omtrent fem sekunder.

- `System disk refresh will start in 3 seconds.`: loggeren har bekreftet refresh. Meldingen `Preforming refresh off disks` vises i tre sekunder.
- `ERR: stop surface-logger and wait for the current sample to finish`: en egen beskjed ber brukeren stoppe logging og vente til pågående måling er ferdig før disk-refresh forsøkes igjen. Beskjeden lukkes med OK.
- Manglende eller ukjent svar: programmet opplyser at refresh ikke ble bekreftet, og henviser til terminalteksten.

Et nytt `Refresh disk Y/N` i feilsvaret sender ikke en ny Y. Programmet stopper ikke logging automatisk. Det gjenåpner heller ikke COM-porten automatisk etter USB-refresh; instrumentets beskjed om å velge port igjen gjelder fortsatt.

Verifisert med 15 grupper maskinkodetester, inkludert de to oppgitte instrumentsvarene, oppdelte svar, manglende svar, gjentatt Y/N, dobbeltklikk under venting, flyttet lasteadresse og tidligere refresh-/parser-/ressurskontroller. Oppstart av GUI-kopien viste Instrument-vinduet uten feildialoger. Instrumentsvarene er simulert; ingen fysisk refresh ble utført i denne kontrollen.

Bygg: `analysis/build_refresh_reply.py`, `analysis/refresh_reply.s`.
Tester: `analysis/test_refresh_reply.py`.

SHA-256: `ba1f6d5ce50a14155199da2d9a48d15bcf0f165bedcc158966889eb3c47cd551`
