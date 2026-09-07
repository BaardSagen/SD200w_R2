# UART Routing (HEF4052 + RS-232 transceiver)

Goal: document how MCU UART (P3.0 RXD, P3.1 TXD) is routed to the PC connector or radio via the HEF4052 analog switch and the LTC1382 RS-232 interface.

Known from code and schematic notes:
- MCU P3.0/P3.1 connect to IC13 (HEF4052) control matrix; the RS-232 side uses IC14 (LTC1382).
- Firmware uses a control latch (via CS7/CS8) to choose PC vs radio routing and power the radio.
- When radio is active, firmware often forces 9600 8N1.

To finalize:
- Label HEF4052 select pins (S0/S1) and inhibit (INH), and map which control latch bits drive them.
- Produce the truth table: S1 S0 ? PC, Radio, (possibly loopback/NC) for both TX and RX paths.
- Confirm default/reset state (where hello goes after reset) so firmware can explicitly route to PC.

Planned firmware API:
- `uart_route_pc()` ? set latch bits to route UART to PC connector
- `uart_route_radio()` ? route UART to radio module
- `radio_power(on)` ? control radio supply (if latched)

Status: pending exact truth table. See `sd208/README.MD` Hardware mapping for preliminary nets. We?ll update this doc after a schematic pass or a quick board probe.
