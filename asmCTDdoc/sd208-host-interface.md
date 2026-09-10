# SD208 Host Interface (for GUI)

For beregningskjeden, enheter, kalibrering og betydningen av rådata, se
[SD208: beregninger og driftkompensasjon](sd208-beregninger-og-drift.md).
Konduktivitetens rådata er allerede omregnet og driftkompensert før
A3/B3/C3-kalibreringen. Rådatafeltet `R` er intern RB-motstand;
lydhastighet i vanlig måleutskrift har feltmerket liten `c`.

Rapportens avsnitt 13 gir alle feltmerker og enheter: C i mS/cm,
P i dbar, turbiditet i FTU og fluorescens i µg/l. SAIV205-feltet O
beregnes i prosent metning i denne fastvaren, selv om databladet
oppgir mg/l. Enheter for optrode/andre opsjoner må knyttes til sensor
og koeffisientsett. Avsnitt 15–16 skiller databladverdier fra
utdataoppløsning og brukerens erfaringsbaserte måleområde.

Denne guiden er laget fra firmware-kildene i repoet og matcher filen `Pyinterface/sd208_interface.py`.

## 1) Serielink

Firmware stotter:
- Baud: 1200, 2400, 4800, 9600, 19200, 38400
- Format: 8N1 eller 7E1

Praktisk start for host:
- Proev `9600 8N1` foerst
- Faar du ingen respons, proev `4800 7E1` og deretter resten av baud-listen

Kilder:
- `sd208-as/SD49INIT.ASM` (`baud_set`)
- `sd208-as/SD49MOD1.ASM` (`dc1=0x11`, `dc3=0x13`)

## 2) Kommandoer du trenger

Passive/wake:
- `I`: aktivering (ofte sendt mange ganger i burst)
- `X`: direkte menyvei fra passiv deteksjon
- `Y`, `Z`, `W`: andre wake-paths brukt i firmware

Fjern/wake-meny (remote):
- `A`: air pressure
- `S`: status/start/menu-flyt
- `H`: passiv

Hovedmeny:
- `F`: dump lagrede data
- `E`: erase data (krever bekreftelse)
- `H`: passiv
- `I`: interval setup
- `R`: start via key-board (run/start)
- `G`: generell back/escape fra menyer/submenyer

Erase-flyt:
- Send `E`
- Instrument svarer med `Erase memory Y/N Menu:<G>`
- Send `Y` for erase, `N` for avbryt, `G` tilbake til meny

Dump-flyt:
- Send `F`
- Les tekststrom til `End of data.`
- Under dump kan `I` eller `G` brukes for avbrudd/retur
- `CTRL-S` (`DC3`, `0x13`) pauser dump
- `CTRL-Q` (`DC1`, `0x11`) fortsetter dump

Hang/recovery:
- Hvis instrumentet virker fast, vent ca. 60 sekunder
- Den gaar normalt tilbake til `- passive -`
- Host kan deretter wake pa nytt med `I`-burst

Kilder:
- `sd208-as/SD49MOD1.ASM` (menu mapping, teksttabeller)
- `sd208-as/SD49MODE.ASM` (`erase_mem`, `dump_data`, `dump_con`)
- `sd208-as/SD49CL.ASM` (`remote_command`)
- `sd208-as/SD249.ASM` (wake/power-down loop)
- `sd208-as/SD49CL.ASM` (`S` i remote flow og `M` i `manual_start`)

## 3) Anbefalt host-flyt i GUI

1. Koble til seriell port.
2. Send `I`-burst i 2-5 sekunder for wake.
3. Etter wake kommer normalt remote-menyen (`A/S/H`).
4. For hovedmeny: send `S`, deretter `M`.
5. Alternativ hurtigvei pa noen enheter: send `X`.
6. For nedlasting: send `F`, les til `End of data.`.
7. For sletting: send `E`, deretter `Y`.
8. For passiv: send `H`.
9. Hvis noe henger: send `G` og vent opptil 60 sekunder pa `- passive -`.
10. For run/start: `S` -> `I`, stopp med gjentatte `I` (evt `G`).

## 4) Bruk Python-filen direkte

Filen du kan legge rett i GUI-prosjekt:
- `Pyinterface/sd208_interface.py`

Den inneholder:
- `Sd208Client` (wake/menu/dump/erase/passive)
- `PySerialTransport` (real COM-port)
- `MockSd208Transport` (utvikling uten instrument)
- `dump_pause_ctrl()` / `dump_resume_ctrl()` for `DC3/DC1`
- `dump_stop("G")` eller `dump_stop("I")`
- `back_g()` for generell escape/back
- `wait_for_passive(65.0)` og `recover_from_hang(...)` for heng-recovery
- `run_start()/run_stop()/run_for()/run_via_status()` for run-flyt
  (`run_via_status` velger `R` automatisk hvis du allerede staar i meny)
- `mock_fill_random(count)` for rask random testdata (mock)
- Mock har full hovedmenytekst og interval/baud/type-range submenyer

Eksempel (Python):

```python
from Pyinterface.sd208_interface import create_client

client = create_client("COM5", baudrate=9600, bytesize=8, parity="N")
print(client.wake_with_i())
print(client.request_menu())
dump_text = client.dump_data()
print(dump_text)
client.dump_pause_ctrl()   # DC3
client.dump_resume_ctrl()  # DC1
print(client.dump_stop("G"))
print(client.erase_data(confirm=True))
print(client.go_passive())
print(client.back_g())
print(client.wait_for_passive(65.0))
print(client.run_via_status(seconds=8.0))
print(client.mock_fill_random(200))
client.close()
```

## 5) Mini-eksempler i C# og C++

C# (`System.IO.Ports`):

```csharp
using System.IO.Ports;
using System.Text;

var sp = new SerialPort("COM5", 9600, Parity.None, 8, StopBits.One);
sp.ReadTimeout = 100;
sp.Open();
sp.Write(new string('I', 32)); // wake burst
sp.Write("S");                 // status/start/menu
sp.Write("M");                 // main menu
sp.Write("F");                 // dump
sp.Write(new byte[] { 0x13 }, 0, 1); // CTRL-S (pause)
sp.Write(new byte[] { 0x11 }, 0, 1); // CTRL-Q (resume)
sp.Write("G");                 // stop dump / tilbake meny
```

C++ (pseudo med valgfri serial-lib):

```cpp
serial.write("IIIIIIIIIIIIIIII");
serial.write("S"); // status/start/menu
serial.write("M"); // main menu
serial.write("F"); // dump
serial.write_byte(0x13); // CTRL-S pause
serial.write_byte(0x11); // CTRL-Q resume
serial.write("G"); // stop dump
serial.write("E"); // erase
serial.write("Y"); // confirm
```

## 6) Verifisert flyt mot fysisk enhet (2026-02-26)

Session med `COM3`, `9600 8N1` er logget i:
- `Pyinterface/logs/com3_session_20260226_210501.log`
- `Pyinterface/logs/com3_session_20260226_210641.log`
- `Pyinterface/logs/com3_session_20260226_211026.log`

Bekreftet:
- `wake_with_i()` ga remote-meny (`A/S/H`).
- `S` ga full status/start-tekst.
- `I` startet run.
- Stopp fra run krevde i praksis gjentatte `I`-burst (`I` x 24) for sikker retur.
- `S` -> `M` ga full hovedmeny.
- `F` dump gikk til `End of data.`.
- `H` ga passiv (`- passive -`), men enkelte bytes kan vaere stoy/garbled rett foer passiv-markoeren.

Praktisk regel:
- Ved treg/ustabil overgang fra run: send flere `I`-burst foer du proever `S`/`M` pa nytt.
