# Serial protocol and menus (draft)

This document will capture the serial commands, menu flows, and output frame formats.

## Known behaviors
- Baud options map to TH1 reloads; radio mode typically uses 9600 8N1.
- `plug_test` determines cable vs radio; `rs_set` applies baud/parity.
- Output is assembled via `output_mode` and paced delays; raw data path via `raw_reorg/data_reorg`.

## To extract
- Menu keystrokes and prompts from SD49MODE.ASM and related modules.
- Response strings from SD49CONV.ASM and SD49CL.ASM message tables.
- Raw/processed frame formats, field order, separators, CR/LF policy.

## Next steps
- Parse message tables and build a command reference with examples.
