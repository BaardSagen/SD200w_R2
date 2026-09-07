# Chip-selects (IC7: 74HC154D) and P1 mapping

This documents how the MCU drives chip-selects through the 4?16 demultiplexer (IC7: 74HC154D) using port P1.0..P1.3.

- P1.0 ? ram_select
- P1.1 ? sel1
- P1.2 ? sel2
- P1.3 ? sel3

These four bits form a nibble P1[3:0] that selects one active-low Y output on the 74HC154.

Observed mapping (from the DipTrace export and code usage):

- Y0 ? CS1  (SRAM bank)
- Y1 ? CS2  (SRAM bank)
- Y2 ? CS3  (SRAM bank)
- Y3 ? CS4  (EEPROM AT28C256)
- Y4 ? CS5  (Clock/RTC block enable)
- Y5 ? CS6  (Control path via inverter)
- Y6 ? CS7  (Control latch path)
- Y7 ? CS8  (Control latch path)
- Y8 ? CS9  (Detect latch path)
- Y9 ? CS10 (LED/status latch path)
- Y10 ? CS11 (ADC control path)

Notes:
- All Y outputs are active-low. Only one Y is asserted (low) for each P1 nibble value.
- RD and WR from the MCU go to the memory and EEPROM OE/WE lines; latches and other peripherals may sample data on WR edges depending on design.
- The exact Y?device nets were verified in the schematic XML; see the main `sd208/README.MD` Hardware mapping section for pin/net references.

Firmware helpers planned/used in C skeleton:
- `cs_write_nibble(y)` sets P1[3:0] to choose Y output.
- `cs_select(CSx)` enumerates the logical CS codes.
- Timing helpers (like `c_on`/`c_off` in ASM) should be mirrored when we begin MOVX I/O with latches and EEPROM.
## Chip selects and control nets (IC7 74HC154)

Finalized mapping extracted from the DipTrace schematic XML (`shematic/xmlexport401.dchxml`) and cross?checked with the firmware usage patterns. This unblocks a clean HAL for C.

### IC7 (74HC154) control signals

- Address inputs A3..A0 (from MCU `U1`, AT89C51RD2, Port 1 lines):
  - A3 = Net 130 ? U1 P1.3 (firmware name sel3)
  - A2 = Net 129 ? U1 P1.2 (firmware name sel2)
  - A1 = Net 128 ? U1 P1.1 (firmware name sel1)
  - A0 = Net 127 ? U1 P1.0 (firmware name ram_select)
  - Evidence: IC7 pins list A3..A0 nets as 130,129,128,127; U1 pins connect to these nets (XML Nets 127?130).
- Enable (active?low) = Net 134 (driven via inverter from Net 52)
  - Evidence: IC7 pin uses Net 134; `IC17` (SN74HC14) Part 1 ties Net 52 ? Net 134. Net 52 is produced by `IC16` (NAND), gating RD/WR.
- 74HC154 outputs are active?low. YN is asserted when binary A3..A0 equals N (0..15).

### CS mapping: IC7 YN ? NetId ? NetPort name ? destination

- CS1 ? NetId 118 ? Y0 ? Destination: IC2 `R1RP0408DGE-2PI#B1` (SRAM bank 0) CE
  - XML: Net 118 Items include IC2 Pin 5, NetPort CS1, IC7 Pin 0 (Y0)
- CS2 ? NetId 119 ? Y1 ? Destination: IC3 `R1RP0408DGE-2PI#B1` (SRAM bank 1) CE
  - XML: Net 119 Items include IC3, NetPort CS2, IC7 Pin 1 (Y1)
- CS3 ? NetId 120 ? Y2 ? Destination: IC4 `R1RP0408DGE-2PI#B1` (SRAM bank 2) CE
  - XML: Net 120 Items include IC4, NetPort CS3, IC7 Pin 2 (Y2)
- CS4 ? NetId 122 ? Y3 ? Destination: IC5 `AT28C256` (EEPROM) CE
  - XML: Net 122 Items include IC5, NetPort CS4, IC7 Pin 3 (Y3)
- CS5 ? NetId 131 ? Y4 ? Destination: IC8 `A3024SO20A+` (Clock/RTC block) control pin (Pin 12)
  - XML: Net 131 Items include IC8 Pin 12, NetPort CS5, IC7 Pin 4 (Y4)
- CS6 ? NetId 55 ? Y5 ? Destination: Routed via `IC17` (SN74HC14 Part 3) to system logic (gated control path)
  - XML: Net 55 Items include `IC17` Part 3, NetPort CS6, IC7 Pin 5 (Y5)
- CS7 ? NetId 132 ? Y6 ? Destination: Routed via `IC15` (SN74HC14 Part 2) to control latch logic
  - XML: Net 132 Items include `IC15` Part 2, NetPort CS7, IC7 Pin 6 (Y6)
- CS8 ? NetId 133 ? Y7 ? Destination: Routed via `IC15` (SN74HC14 Part 3) to control latch logic
  - XML: Net 133 Items include `IC15` Part 3, NetPort CS8, IC7 Pin 7 (Y7)
- CS9 ? NetId 56 ? Y8 ? Destination: `IC11` 74HC573 (address/data/control latch) OE path (read/detect)
  - XML: Net 56 Items include `IC11` Pin 8, NetPort CS9, IC7 Pin 8 (Y8)
- CS10 ? NetId 41 ? Y9 ? Destination: Front?panel/LED latch path via `IC18` (inverters) on Sheet 0
  - XML: Net 41 Items include NetPort CS10 (Sheet 0/1), IC7 Pin 9 (Y9), and `IC18` Part 3/NetPort16
- CS11 ? NetId 43 ? Y10 ? Destination: Analog/ADC control path (via `IC18` inverters on Sheet 0)
  - XML: Net 43 Items include NetPort CS11 (Sheet 1), IC7 Pin 10 (Y10), and `IC18` Part 4; used by firmware as ADC CS
- Y11..Y15 are not used (NC in the schematic symbol).

Notes
- Firmware naming aligns: P1.0=ram_select, P1.1=sel1, P1.2=sel2, P1.3=sel3. The binary value on [sel3..ram_select] selects YN (active?low).
- `c_on/c_off` routines gate the 74HC154 enable through an inverter (Net 134), synchronized with MOVX cycles.

### HEF4052 (IC13) UART/radio routing ? control nets (for reference)

While not a chip?select from IC7, these control nets are adjacent to CS use and relevant for the comms HAL:
- IC13 `HEF4052` pins and nets of interest (from XML):
  - Control lines from MCU: Net 155 ? IC13 Pin 4; Net 156 ? IC13 Pin 5 (select A/B)
    - XML: Net 155 Items include IC13 Pin 4 and U1 (Part 410) Pin 5. Net 156 Items include IC13 Pin 5 and U1 Pin 4.
  - Common I/O between HEF4052 and RS?232 transceiver `IC14` (LTC1382):
    - Net 161 ? IC13 Pin 8 ? IC14 Pin 9 (one UART path)
    - Net 162 ? IC13 Pin 10 ? IC14 Pin 10 (the other UART path)
  - Additional channel I/Os towards radio/TTL: Net 159, 160, 170, 171 (see XML around IC13/IC14 for exact pin associations).

To do (minor):
- Finish labeling IC13 control signal names (S0/S1/INH) against nets 155/156/148 by cross?checking the library?s pinout.
- Add final destinations for CS6?CS8 inverter?routed paths once the downstream gates/latches are fully enumerated.

Cross?references (XML evidence)
- IC7 74HC154 Part Id=60 pins show Nets: Y0..Y10 ? 118,119,120,122,131,55,132,133,56,41,43; Enable ? 134; A3..A0 ? 130,129,128,127.
- NetPorts on Sheet 1: CS1=118, CS2=119, CS3=120, CS4=122, CS5=131, CS6=55, CS7=132, CS8=133, CS9=56, CS10=41, CS11=43.
- Device ties: IC2/IC3/IC4 (SRAMs) on CS1/CS2/CS3 respectively; IC5 (AT28C256) on CS4; IC8 (A3024SO20A+) on CS5; IC11 (74HC573) on CS9.
