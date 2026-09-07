# Hidden U configuration update in OSU107 mode

## Agreed behavior

U remains unadvertised in the OSU107 passive/start greeting. It invokes the
existing local MIR + APPLY action even when the external instrument is sleeping
or absent. The existing instrument main-menu U and Surface U remain available.
Instrument submenus and OSU local confirmation dialogs retain their input.
During logging the shortcut asks the operator to stop first.

## Implementation

- `instrument_update_config_policy.hpp`: explicit routing decisions for hidden
  U, main-menu U, busy logging, and dialogs that own the key.
- `SD204_8_Instrument::hasInteractiveCommandContext`: uses latched protocol/input
  state rather than an expiring communication hold, so long silent numeric
  prompts and self-test retain their keys.
- `services_wiring_bootstrap.cpp`: runs the existing configuration action locally.
  After applying, presents Surface if that is the new mode. G is sent only when
  returning to an already active instrument main menu; the sleeping/absent path
  does not attempt to wake or query the external instrument.
- No greeting/menu text or configuration file format was changed.

## Validation

Host routing regression passed for disabled instrument mode, passive/absent
instrument, running logging, long-lived submenu state, main menu, and local
confirmation dialogs. PCB 3.1.2 firmware build passed, followed by app-only
flash and verification through J-Link 69650428. SN107 / COM11 verified build
`Sep 07 2026 15:10:37` (0.9.9P, working tree based on main@602becb1).

Hardware checks passed:

- Unadvertised raw U from the passive greeting ran MIR + APPLY without waking
  the instrument or returning its menu; unchanged configuration reported success.
- Changed only surface.enable=1 and instrument0.enable=0 in system.ini. Hidden
  U applied both and immediately presented the stopped Surface menu.
- Restored the original system.ini bytes and used existing Surface U to return
  to OSU107 without requesting an instrument menu. Final disk file matches the
  original backup byte-for-byte; APPLY reported no remaining NVS differences.
- U inside the T submenu was forwarded to the instrument (its existing illegal
  input response appeared); no local UPDATE_CONFIG ran.
- Existing main-menu U still applied and returned the instrument main menu.
- During actual 5-second measurements, U returned `Stop logging before Update
  config changes.` without starting MIR/APPLY. Measurement was then stopped
  and passive state confirmed.
- Lowercase u plus Enter worked after the normal F/Y disk refresh.

The existing stale-host-cache protection rejected an immediate post-measurement
MIR before disk refresh. The existing repair attempt also refused because the
firmware still owned the disk, leaving configuration unchanged. F/Y refresh and
CDC reconnect cleared that condition; U then succeeded. The shortcut intentionally
retains the existing disk protections and does not replace disk refresh.

Evidence: workspace `tmp/hidden_u_after.log`, original file backup
`tmp/hidden_u_system_original.ini`. Final configuration is the original OSU107
mode, Surface stopped, external instrument passive, and COM11 released.
Physical cable removal was not needed for this test; absence uses the same local
route with no instrument wake/query and is covered by the routing regression.
