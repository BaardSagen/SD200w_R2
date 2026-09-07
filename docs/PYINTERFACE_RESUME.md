# SD208 Pyinterface Resume (2026-02-26)

Denne filen er en kort status for aa kunne bytte fokus/prosjekt og komme raskt tilbake senere.

## Hva som er pa plass

- `Pyinterface/sd208_interface.py` er utvidet med:
  - run/start-stop helper-funksjoner (`run_start`, `run_stop`, `run_for`, `run_via_status`)
  - dump-stop med preferanse for `G` (fallback `I`)
  - recovery helpers (`back_g`, `wait_for_passive`, `recover_from_hang`)
  - mock random data generator (`mock_fill_random` / `fill_random_data`)
  - utvidet mock state machine (main menu + interval/type/range/baud submenyer)
- `Pyinterface/gui_test_sd208.py` har GUI-knapper for run/recovery/mock-fill + live CLI uten CR/LF.
- `Pyinterface/com3_probe.py` lager repeterbar HW-probe med tidsstemplet TX/RX-logg.
- Dokumentasjon oppdatert i:
  - `docs/sd208-host-interface.md`
  - `Pyinterface/README.md`

## HW-verifisering (26.02.2026)

Kjoert mot fysisk instrument paa `COM3`, `9600 8N1`.

Loggfiler:
- `Pyinterface/logs/com3_session_20260226_210501.log`
- `Pyinterface/logs/com3_session_20260226_210641.log`
- `Pyinterface/logs/com3_session_20260226_211026.log`

Flyt som ble bekreftet:
1. `I`-wake -> remote meny (`A/S/H`)
2. `S` -> status/start
3. `I` -> running
4. run-stop via gjentatte `I`-burst (noen ganger flere forsok)
5. `S` -> `M` -> full hovedmeny
6. `F` -> dump til `End of data.`
7. `H` -> `- passive -`

## Hurtig oppstart senere

```powershell
cd Pyinterface
pip install -r requirements.txt
python gui_test_sd208.py
```

For fysisk test med logg:

```powershell
cd Pyinterface
python com3_probe.py
```

## Kjente praktiske forhold

- Run-stop er ikke alltid ett enkelt tastetrykk; bruk `I`-burst ved behov.
- Ved heng: `G` + vent opptil ca. 60 sekunder paa passiv (`- passive -`).
- Passiv-respons kan av og til ha garbled bytes rett foer passiv-markoer.

## Naturlige neste steg

1. Legg til valgfri COM-port parameter i `com3_probe.py` (CLI-arg i stedet for hardkodet `COM3`).
2. Legg til enkel parser i GUI for aa telle dump-linjer (`Nxxxxx`) og vise antall.
3. Legg til `.gitignore`-regel for `__pycache__/` og eventuelt `Pyinterface/logs/*.log` hvis loggene ikke skal versjoneres.
