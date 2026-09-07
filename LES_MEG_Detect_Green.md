# Lys grønn markering ved instrumentfunn

Bruk `SD200W_SAIV_OSU107_Detect_Green.exe`.

Resultatfeltet i Detect får lys grønn bakgrunn (#D8F2D8) når minst ett
ferdig søk har gjenkjent et SD200-instrument. Dette er en felles markering
for resultatfeltet, ikke individuell fargelegging av hver portlinje.
Searching, GPS, Modem, Unknown, Busy og Error utløser ikke markeringen.
Bakgrunnen tilbakestilles når et nytt søk starter.

Tidligere endringer er bevart. Forrige programkopi er ikke overskrevet.

Kontrollert: 18 simulerte tilfeller, inkludert flyttet lasteadresse;
faktisk oppstart, Detect/avbryt og Setup/avbryt uten feilmeldinger;
begge fargeegenskapene oppdateres ved simulert funn i separat testkopi.
Skjermfangst på privat skrivebord ble svart og ga ikke visuell validering.
Funn mot fysisk instrument er ikke testet her.

Bygg: `analysis/build_detect_green.py`.
Kontroll: `analysis/check_detect_green.py` og
`analysis/detect_green_validation.json`.
