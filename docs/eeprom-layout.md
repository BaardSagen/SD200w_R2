# EEPROM layout ? SD204/SD208

This document sketches the EEPROM organization as implied by `SD49INIT.ASM` (eeset_coeff/eepre_coeff) and helpers.

## Header / control
- Address 0x0000: 0x55 (signature)
- 0x0001: exs_buff+4 (2.5 s period counter)
- 0x0002: exs_buff+5 (multiple)
- 0x0003: exs_buff+6 (rest)

## Config pointers (written via new_pointer/new1_pointer)
- baudsel, switch_pos (interval), channel (mode), sampling[0..2] (battery counters)
- opchannel_1, opchannel_2, rawpek, con_fig (parity/data)
- aut_rang, op_regist, ox_regist
- radiodet, radiopt, radiobuoy, hourtime+2, select_4_8 (SD208/SD204)

These are serialized via `ne_po`/`new_poinut` and placed sequentially after 0x0003.

## Coefficients
- Coefficients are written in blocks of 8 or 10 bytes each (ASCII segments), with `write_eep` called on 64?byte boundaries.
- The order mirrors `eeco_buff` calls; effectively the same order as `coef_tbl1` definitions.
- Use `co_buffer`/`co_buffer8` to determine exact paging and addresses; add a table here once extracted.

## Next steps
- Instrument `co_buffer` address increments to record actual addresses.
- Generate a coefficient address map (symbol ? EEPROM address range).
