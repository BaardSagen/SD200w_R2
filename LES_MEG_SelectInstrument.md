# Enklere instrumentvalg

Program: `SD200W_SAIV_OSU107_SelectInstrument.exe`

Bygger videre på LoggerDetect-versjonen. Tidligere programfiler er beholdt.

- Ett klikk på en rad setter denne til `Instr` og fjerner instrumentvalget fra den tidligere raden.
- OK bekrefter valget som før.
- Dobbeltklikk velger raden og aktiverer den samme OK-knappen.
- Instrument, Aux, None og teksten «Use selected as» er skjult og ute av tabulatorrekkefølgen.
- En eksisterende grensefeil som avviste siste rad er rettet.

GUI-test 7. september 2026 kontrollerte bytte mellom rader, også siste rad, bare ett `Instr`-valg, skjulte knapper, dobbeltklikk og vanlig OK. Setup viste COM7 etter dobbeltklikk-testen og COM11 etter OK-testen. Ingen feildialoger ble observert i de beståtte testene. En første OK-test ventet for kort på avslutning av pågående portsøk; testen ble gjentatt med lengre ventetid og bestod uten ytterligere programendringer.

Bygg: `analysis/build_select_instrument.py` og `analysis/select_instrument.s`.
Test: `analysis/check_startup_windows.py --select-test`, med `--select-last --select-ok` for siste rad og OK.
Rapporter: `analysis/runtime_test/select_double_click.json` og `analysis/runtime_test/SD200W_SAIV_OSU107_SelectInstrument.json`.

SHA-256: `f726c144d92c82d9ae89e92efcdf49deb0e523d23805370fd4b1f6125dc6c802`
