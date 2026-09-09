# SD200W 1.0.2 – kreditering og disclaimer

Dato: 8. september 2026.

Program: [SD200W_SAIV_v1.0.2_Sept2026.exe](SD200W_SAIV_v1.0.2_Sept2026.exe).

Dette er en ny kopi basert på 1.0.1. Tidligere leveranser er beholdt.

## About

Developer-feltet er erstattet av:

1. Concept and technical specifications: SAIV AS
2. Original software development: Morten Hammersland Programvare
3. Further development and maintenance: SAIV AS

## Disclaimer

Disclaimer:

Always keep backup copies of your data files and verify measurement results before relying on them.

To the extent permitted by applicable law, neither SAIV AS nor Morten Hammersland Programvare shall be liable for loss of data, loss of profits or indirect damages arising from the use of this software.

This notice does not override any applicable contractual obligations or mandatory legal rights.

## Kontroll og videre arbeid

About-vinduet er utvidet. Begge dialogene er åpnet og lukket i en egen testprosess, og skjermbildene er visuelt kontrollert. Disclaimerens ordrette tekst ble også lest fra testprosessens minne. PE-sjekksum, DFM og Windows-versjonsfelt er kontrollert. Formler og kommunikasjon er bevart.

Bygg: `python analysis/build_credits_disclaimer.py` (krever 1.0.1 med forventet hash og `pefile`). Bygget skriver den navngitte 1.0.2-filen; kjør i en egen kopi ved gjenskaping. GUI-kontroll: `python analysis/check_credits_windows.py --live`, som åpner og avslutter bare sin egen testprosess. Uten `--live` brukes privat desktop, der skjermbilder kan bli svarte.

SHA-256: `e9f6a7fef0c34537ab32e1d0797d74716e67cd701587de66b3b5a305262424e6`.

Denne leveransen er lokal; GitHub-opplasting er ikke utført.
