# SAIV Instrument Terminal 1.3.2 - husk siste COM-port

Lokal leveranse 9. september 2026. Start **SAIV_Instrument_Terminal_v1.3.2_Sept2026.exe**. **SIT_Import131.dll** skal fortsatt ligge i samme mappe. Hele pakken finnes i **SAIV_IT_v1.3.2_portable.zip**.

## Endringen

Siste bekreftede COM-port lagres umiddelbart via programmets eksisterende innstillinger under HKCU\Software\MHP\SdInstr\Comm, verdien Port. Ved neste start brukes denne porten. Dette gjelder bekreftet portvalg fra Setup og fra Detect. Avbryt i Setup endrer ikke den lagrede porten. Lagringen er per Windows-bruker og PC.

Den gamle oppstartskoden leste allerede Comm/Port. Feilen var at Setup hoppet over skriving dersom porten allerede var satt, slik SD200-valget fra Detect kan ha gjort. Den nye kroken skriver gjeldende COM-port ved bekreftelse selv om portendringsflagget er av. IP-modus, port 0 og manglende objekter utelates. Den eksisterende Show startup text-kroken viderefores.

## Tester

- Den gamle feilen er reprodusert i 1.3.1: aktiv COM7, lagret COM11.
- 1.3.2 lagrer COM7 i samme situasjon og leser COM7 ved omstart.
- Manuelt portvalg COM11 lagres og leses ved neste omstart.
- Avbryt etter et annet portvalg beholder COM7.
- 16 maskinkodetester for port 7/11/255, port 0, IP, manglende objekter, registre/stakk og alternativ lasteadresse bestod.

GUI-testen brukte eget midlertidig registeromrade og egne prosesser. Fysisk portaapning var deaktivert i testprosessene. Detect-tilstanden ble gjenskapt med den opprinnelige native portsetteren, ikke med en ny fysisk instrumentskanning. Brukerens innstillinger er ikke endret. Rapporter: analysis/runtime_test/last_port132/gui_validation.json og analysis/last_com_port_validation.json.

UART, autodetekt, G-timer, sensorformler og Convert/Merge er ellers byte-identiske med 1.3.1. Convert/Merge-modulen er fortsatt versjon 1.3.1, og dens eksportheader viser derfor fortsatt 1.3.1. Programmet og About/Windows-versjonen viser 1.3.2. Ingen fysisk instrumenttest eller GitHub-push er gjort.

Bygg: python analysis/build_last_com_port.py. Kode: analysis/last_com_port.s. Bygggrunnlag er bevart 1.3.1 med hashkontroll. Eldre leveranser er beholdt.
