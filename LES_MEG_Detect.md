# MiniSoft med Detect i Instrument-vinduet

Bruk `SD200W_SAIV_OSU107_Detect.exe`.

Detect ligger rett under Print og åpner programmets eksisterende instrumentsøk.
Ved godkjent søk brukes den eksisterende lagringen og oppdateringen av
kommunikasjonsinnstillingene. Avbryt går tilbake til terminalen.
Detect under Setup er fortsatt tilgjengelig.

Denne kopien bygger på History-utgaven og beholder tidligere endringer,
inkludert utvidet terminalhistorikk og korrigert oppstart i Instrument.
History-utgaven er ikke overskrevet.

Kontrollert med faktisk programkjøring på et privat Windows-skrivebord:
oppstart i Instrument, åpning og avbryt av direkte Detect, samt åpning og
avbryt av vanlig Setup. Ingen feilmeldinger under denne testen.
Godkjent søk, avbryt og vanlig Setup er også kontrollert med simulert kjøring
av brokoden ved to lasteadresser. Fysisk instrumentdeteksjon er ikke verifisert.

Byggeskript: `analysis/build_terminal_detect.py`.
Validering: `analysis/terminal_detect_validation.json` og
`analysis/runtime_test/SD200W_SAIV_OSU107_Detect.json`.
