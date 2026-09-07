# SD208 A2 ? how to resume later (playbook)

This note captures the minimum steps to pick up the A2 refactor at a later date, with pointers to code and build outputs.

## Quick start
- Tools: Keil A51/BL51/OH51 are bundled under `programmingTool/C51/BIN`.
- Build:
  1) Open a terminal at `sd208_a2/` and run `build.ps1`.
  2) Artifacts are written to `sd208_a2/out/` (ABS, M51, HEX).
- Entry points:
  - Core logic: `sd208_a2/src/SD49INCL_A2.ASM` (navigator header at top lists ported branches).
  - Tables: `sd208_a2/src/tables*.asm` (`s_tbl*` and `det_tbl*` PUBLIC symbols).
  - Stubs: `sd208_a2/src/a2_stubs.asm` (bits/DATA/XDATA and minimal call placeholders).

## Current status (2025-09-27)
- Ported branches: set_ins; se_ins3?9; se_in10; s_end/s_end2, with all required helpers.
- No branch stubs for these remain; only I/O/data stubs remain.
- Clean builds: 0 warnings/0 errors; HEX ? 13,104 bytes.
- `build.ps1` prints a post-build summary of referenced `s_tbl*`/`det_tbl*` to show progress even when size is unchanged.

## Recommended next steps when resuming
1) Hygiene
   - Trim unused `EXTRN CODE (...)` lines in `SD49INCL_A2.ASM` once verified unused across modules.
   - Add a glossary comment for `buffer+N`, and bit flags mapping (plug_bit/op_mes/hele_bit/optr_bit/turb*_bit).
2) Readability (no behavior change)
   - Introduce EQU alias labels for opaque names (keep originals for compatibility).
   - Add a compact ?decision map? for se_ins* in `sd208_a2/refactor-notes.md` or here.
3) De-stubbing (incremental)
   - Replace call stubs (`plug_test`, `mess_out`, `dump_out`, `outp_cl`) with real glue as available.
   - Convert any remaining DATA/XDATA stubs to real symbols once their sources are ported.
   - Verify via clean build and inspect HEX/M51 deltas at each step.

## Git pointers
- All A2 work is already merged on `main` (no feature branch kept).
- Tag created: `a2-parking-2025-09-27` marks the end of this session for easy checkout.

## Troubleshooting
- If build tools are missing, verify `programmingTool/C51/BIN` exists and `build.ps1` resolves it.
- If line ending warnings appear, they are harmless; scripts don?t modify sources, only print a post-build summary.

## Strategic recommendation (when resuming)
- Prioritize transitioning decision logic to C while keeping a small ASM core only where timing is critical (ISRs, bit-bang, tight serial timing).
- Benefits: maintainability, testability (unit tests, static analysis), and easier evolution of decision tables without fragile timing.
- Suggested hybrid plan:
   1) Keep A2 as the behavior reference (?golden?) and source of truth for tables.
   2) Export `s_tbl*`/`det_tbl*` as `const` in C with the same layout/indices.
   3) Port se_ins* branches to C gradually; retain original label names as comments for traceability.
   4) Maintain ASM only for critical timing; measure and verify with HEX/M51 deltas and on-hardware checks.
   5) Mind Keil C51 details: memory model (small/compact/large), `bit` variables, ISR/reentrancy qualifiers, and C/ASM call conventions.
