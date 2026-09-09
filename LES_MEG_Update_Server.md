# Oppdateringsserver - klargjort paa branch update

Programmet til og med 1.4.0 er sikret i commit 6d668c5. Foerste manifestutkast er sikret i 30ed32e paa feature/import-all-fields. Videre oppdateringsarbeid foregaar paa update.

## Legg disse tre filene i https://saiv.no/software/

- update_server/SAIV_Instrument_Terminal_v1.4.2_Sept2026.zip
- update_server/README_v1.4.2.txt
- update_server/latest.json

Last opp ZIP og README foerst, deretter latest.json. Filene skal kunne hentes uten innlogging. Bruk UTF-8 for JSON og README. latest.json boer ha kort cachetid eller Cache-Control: no-cache, slik at en eldre versjonsoversikt ikke blir liggende i mellomlagring.

ZIP inneholder levert 1.4.2-EXE, README.txt og THIRD_PARTY_NOTICES.txt. Kunden trenger fortsatt bare EXE-en; nodvendige komponenter og lisens er innebygd. Den eksterne README-filen er identisk med README.txt i ZIP-en. Kundeinformasjonen er paa engelsk. Eldre serverpakker beholdes. Pakking og hashkontroll: analysis/prepare_update_server_142.py.

## Format

latest.json inneholder version, url, readme_url og sha256. Version er et numerisk punktdelt versjonsnummer. URL peker paa ZIP-en; readme_url peker paa ren tekst som skal vises i programmet. SHA-256 gjelder hele ZIP-filen. Ved ny leveranse opprettes en ny ZIP og versjonsspesifikk README, og latest.json oppdateres med versjon, lenker og ny hash. Behold gjerne eldre pakker.

## Program og serverstatus

1.4.1 har oppstartssporsmaal foer nett, lagret av-hake, Help > Update software, README-vindu og automatisk installasjon etter bekreftelse. Les LES_MEG_Update_141.md. Versjon 1.4.0 og eldre maa oppgraderes manuelt EN gang for aa faa denne funksjonen.

Brukeren har publisert 1.4.0-filene. Alle tre er kontrollert offentlig med HTTP 200 og korrekt innhold/kontrollsum. En separat testklient har provd hele nedlastings- og installasjonsflyten mot disse serverfilene. Ny 1.4.1-pakke er bare klargjort lokalt: last opp ny ZIP og README, og erstatt latest.json til slutt. Vi har ikke endret serveren eller pushet Git.

Naar serveren har 1.4.1, vil en 1.4.1-klient korrekt vise ingen nyere versjon. Ved neste reelle versjon endres version, url, readme_url og sha256 samlet. SHA256 i den genererte filen er smaabokstaver. ZIP-ens programfil skal ha samme navn som ZIP-en med .exe i stedet for .zip, og innebygd versjonsnummer skal stemme med version.

1.4.2 er naa klargjort som oppdateringstest fra 1.4.1. Les LES_MEG_Update_Test_142.md. Nye brukere kan bruke ZIP/EXE direkte.
