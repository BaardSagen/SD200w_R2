# Oppdateringsserver - klargjort paa branch update

Programmet til og med 1.4.0 er sikret i commit 6d668c5. Foerste manifestutkast er sikret i 30ed32e paa feature/import-all-fields. Videre oppdateringsarbeid foregaar paa update.

## Legg disse tre filene i https://saiv.no/software/

- update_server/SAIV_Instrument_Terminal_v1.4.0_Sept2026.zip
- update_server/README_v1.4.0.txt
- update_server/latest.json

Last opp ZIP og README foerst, deretter latest.json. Filene skal kunne hentes uten innlogging. Bruk UTF-8 for JSON og README. latest.json boer ha kort cachetid eller Cache-Control: no-cache, slik at en eldre versjonsoversikt ikke blir liggende i mellomlagring.

ZIP inneholder den allerede leverte 1.4.0-EXE-en og README.txt. Den eksterne README-filen er identisk med README.txt i ZIP-en. Kundeinformasjonen er paa engelsk. Den beskriver faktiske endringer fra 1.3.6, og sier uttrykkelig at nettoppdateringsfunksjonen ikke er med i denne utgaven.

## Format

latest.json inneholder version, url, readme_url og sha256. Version er et numerisk punktdelt versjonsnummer. URL peker paa ZIP-en; readme_url peker paa ren tekst som skal vises i programmet. SHA-256 gjelder hele ZIP-filen. Ved ny leveranse opprettes en ny ZIP og versjonsspesifikk README, og latest.json oppdateres med versjon, lenker og ny hash. Behold gjerne eldre pakker.

## Videre programarbeid

Planlagt: Sporsmaal foer nettkontakt ved oppstart, hake for aa slaa av oppstartssjekk, og Help > Update software for manuell kontroll og endring av valget. Nyere versjon skal vises med README i et rullbart vindu, Last ned og Senere. Manglende README skal ikke blokkere nedlastingslenken. Versjoner sammenlignes numerisk. Nettfeil skal ikke blokkere vanlig instrumentbruk.

Oppdateringssjekken er ikke implementert ennaa, og serverfilene er ikke lastet opp av oss. Publisering og faktisk HTTPS-test gjenstaar. 1.4.0-manifestet vil korrekt gi ingen nyere versjon for en klient med versjon 1.4.0 eller hoeyere; testen av et oppdateringstilbud maa bruke en eldre testklient eller en separat testoversikt.
