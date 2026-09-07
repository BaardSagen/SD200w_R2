# Renset program og korrigert refresh-tekstbehandling

Program: `SD200W_SAIV_OSU107_Clean.exe`.
Bygger videre på Refresh-versjonen. Tidligere programkopier er beholdt.

Direkte identitetsrester er fjernet fra den nye EXE-filen:

- Den gamle sertifikatblokken på 8352 byte er nullstilt. Signaturreferansen var allerede fjernet i tidligere modifiserte versjoner.
- Windows-filinformasjonens gamle copyright-navn er erstattet med SAIV A/S.
- Gamle eksempeladresser og avsendernavn i aktive og tidligere kopier av Delphi-ressursene er erstattet med SAIV-navn/adresse.
- Hele EXE-filen er kontrollert for de tidligere navnene, etternavnet, e-postdomenet og programvarebetegnelsen i ASCII, UTF-16LE og UTF-16BE, uten gjenværende treff.

Dette er ikke en garanti mot gjenkjenning av kodeopprinnelsen. Delphi-komponentnavn, maskinkode og strukturell likhet med tidligere utgaver kan fortsatt sammenlignes. Tidligere EXE-filer og analysedokumenter er ikke renset.

Når oppstartsteksten identifiserer OSU107 eller SAIV110 på instrumentporten, behandles Download-svaret som refresh-prosa fra «Data logged by ...» eller den konkrete «Stop logging before refreshing the disk»-linjen. Disse linjene sendes ikke til den gamle måleparseren som åpnet «Error in ref line». Identiteten nullstilles når instrumentporten lukkes. Normal menykommunikasjon, Log og eldre instrumenters måleparser er beholdt.

«Refresh disk Y/N» utløser fortsatt én Y og meldingen «Preforming refresh off disks». Enheten kan avvise refresh under aktiv logging; denne endringen stopper ikke logging automatisk.

Verifisering: ti grupper maskinkodetester bestod, inkludert begge loggeridentiteter, teksten i den rapporterte feilen, ukjent instrument, Log, portbytte, fragmenterte svar, gjentatt refresh og flyttet lasteadresse. Alle aktive Delphi-formressurser kan parses. GUI-oppstart viste Instrument-vinduet uten feildialoger. Den nye filterflyten er testet med simulerte instrumentsvar; fysisk disk-refresh er ikke utført i denne kontrollen.

Bygg: `analysis/build_logger_clean.py`, `analysis/logger_refresh_clean.s`.
Tester: `analysis/test_logger_clean.py`.

SHA-256: `6e85e29b24200ffc5c57084ab9bd51489d6a71da01b8800ac851145b420d6779`
