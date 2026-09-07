# ASM Firmware Overview (SD204/SD208)

Modules:
- SD49CL.ASM ? main program: startup (cold/warm), modes (manual/interval), sensor loop, memory banking, output, power mgmt.
- SD49CONV.ASM ? messages and conversion of ASCII coefficients to binary floats.
- SD48MAT.ASM ? calculations for P/T/C/S/O2/optional sensors.
- SD48MAT1.ASM ? math primitives and constants, serial IO helpers, radio power/config.
- SD249.ASM ? UI + ADC bit-banged I/O (SCL on P1.4, SDATA on P3.5, DRDY on P3.3), sensor sequencing, formatted output.
- SD49INCL.ASM / SD49INCLs ? common equates and port bit naming.

Key hardware lines from ASM:
- P1.0..P1.3 ? demux select (ram_select, sel1..sel3)
- P1.4 ? scl (ADC clock)
- P1.5 ? ep (EEPROM enable)
- P1.6 ? conf (confirm switch)
- P1.7 ? start_con (start conversion)
- P3.3 ? drdy (ADC data ready)
- P3.5 ? sdata (ADC data)

Notable routines (names may vary slightly):
- EEPROM: `eep_start`, `eeset_coeff`, `eepre_coeff`
- ADC: `sdat_out` (20-bit shift), `drdy` wait, `adc_init`
- Radio/serial: `rs_set`, `radio_on/off`, `radi_set`, `plug_test`
- Memory/latch timing: `c_on`, `c_off`, `data_clear`

Migration notes:
- Create a HAL layer for chip-select and MOVX timing; mirror delays where required.
- UART, ADC bit-bang, and EEPROM drivers can be ported module-by-module, with tests that compare outputs to the legacy assembly routines.
