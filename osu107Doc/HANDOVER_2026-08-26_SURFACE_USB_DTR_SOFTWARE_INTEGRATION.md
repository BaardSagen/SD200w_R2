# SAIV110/OSU107 software integration handover: Surface naming and USB DTR information

Date: 2026-08-26

Last updated: 2026-08-27

Firmware: `0.9.9M`

Target: `osu_m_3-1-2`

Git main merge: `1c8c662` (`Merge scheduleTosurface into main`)

Feature commit: `181a863` (`Rename schedule logger to surface and add USB info policy`)

This document describes the latest interface changes that the companion PC software must support. It is a delta to `HANDOVER_2026-08-20_SOFTWARE_INTEGRATION.md`; the earlier handover remains valid for status storage/sensor lines, CTD clock input and synchronization, passive forwarding, configurable tilt fields, and configuration apply behavior.

## Required software changes

1. Rename the user-facing and canonical configuration concept from **schedule** to **surface**.
2. Write `[surface]`, `/surface`, and the `SUR*` commands for firmware `0.9.9K` and later.
3. Add a `usbDtrInfo` setting independently under `[surface]` and `[instrument0]`.
4. Set the software default for `usbDtrInfo` to `both`.
5. Parse the USB-open information as optional, asynchronous terminal text. It is not a handshake and must never block measurement parsing.
6. Do not expect an `Instrument: Active` or `Instrument: Passive` line. Those lines are intentionally absent.
7. When `usbDtrInfo=both`, accept measurement rows immediately after the information message without treating the message as an interruption or a new logging session.
8. Add `compact+DT` to the storage-format choices for both logger modes and use the final `DATE` and `TIME` fields described below.
9. Use `compact+DT` when the software creates a new surface or instrument configuration.
10. Treat `SAIV110` as the surface-only user-facing identity. Keep `OSU107` for instrument mode; instrument remains dominant when both are enabled.
11. Accept surface and instrument menu/prose lines wrapped at a maximum of 72 characters. Measurement rows are not wrapped or changed.

## Schedule-to-surface migration

The current canonical names are:

| Before `0.9.9K` | From `0.9.9K` |
|---|---|
| `[schedule]` | `[surface]` |
| `/schedule` | `/surface` |
| Schedule logger | Surface logger |
| `SCH` | `SUR` |
| `SCHSTART` | `SURSTART` |
| `SCHSTOP` | `SURSTOP` |
| `Mode: Schedule-logger` | `Mode: Surface-logger` |

The default surface data folder is `/surface`. Surface measurement records still use their existing `S...` record format; this change does not rename or alter measurement row prefixes.

Firmware `0.9.9K` accepts legacy `[schedule]` and `/schedule` values during migration and rewrites the configuration in canonical surface form. The NVS numeric IDs were retained, so this rename does not intentionally erase existing NVS data.

Companion-software rules:

- Write only `[surface]`, `/surface`, `SUR`, `SURSTART`, and `SURSTOP` for current firmware.
- It is acceptable to read/import old `[schedule]` configuration for older installations, but convert it to the internal `surface` data model.
- Do not perform a blind text replacement of ordinary programming terms such as `schedule()` or `reschedule()`; only logger/configuration terminology changed.
- Instrument mode remains dominant when both `[instrument0]` and `[surface]` are enabled.

## Surface start/stop terminal text

Starting surface logging with `<I>` now returns:

```text
Starting, Type <I> again for stop or <M> for menu
```

Stopping surface logging with `<I>` now returns:

```text
Stopped, Type <I> again for start or <M> for menu
```

The software may display these lines verbatim. State detection should preferably use the leading `Starting,` or `Stopped,` token rather than column positions.

## New compact storage mode with date and time

Both `[surface]` and `[instrument0]` now accept a third `diskFormat` value:

```ini
diskFormat=compact+DT
```

`compact+DT` retains the existing compact TIMEBASE/value-only behavior, then appends
the measurement date and time as the final two fields in every stored row:

```text
FIELDS: COUNT;Par;OxR;Tilt;DATE;TIME
1;4.47;0.29;2;2026-08-26;13:55:18
```

Instrument example:

```text
FIELDS: COUNT;C;T;P;OX;OT;OS;Par;OxR;Tilt;DATE;TIME
1;00.000;23.758;0001.06;028.80;000.02;000.46;4.44;0.29;2;2026-08-26;13:57:33
```

Contract:

- Canonical value: `compact+DT`; parsing is case-insensitive.
- `DATE` format: `YYYY-MM-DD`.
- `TIME` format: `HH:MM:SS`.
- `DATE` and `TIME` always follow all measurement values.
- If a timestamp component is unavailable, its stored value is `n/a`; column count remains stable.
- Existing `full` and `compact` files are unchanged.
- Live CDC/UART measurement rows are unchanged.
- `compact+DT` belongs to the compact family and keeps the `_C.txt` filename suffix.
- The configured separator is used consistently in both `FIELDS:` and data rows.
- New/missing surface and instrument storage settings default to `compact+DT`.
- An explicit valid format already stored in NVS or `system.ini` is preserved.

Companion software should expose `full`, `compact`, and `compact+DT` for both logger
modes and parse compact columns from `FIELDS:` rather than assuming a fixed sensor layout.
The layout was physically verified on hardware SN107 in both surface and instrument mode.

## Mode-specific product identity and terminal width

- Surface-only mode (`surface.enable=1`, `instrument0.enable=0`) displays `SAIV110` in
  greetings, menus, status/config output, prompts, update results, and stored surface headers.
- Instrument mode displays `OSU107`.
- If both modes are enabled, instrument mode is dominant and the displayed identity is `OSU107`.
- Surface and instrument menu/prose output is word-wrapped to at most 72 characters. Existing line
  endings and blank lines remain meaningful. Live `S...` and `N...` measurement rows are
  never passed through this wrapper.
- Surface `<U>` reports `SAIV110_UPDATE_CONFIG`; instrument `<U>` reports
  `OSU107_UPDATE_CONFIG`.

Both logger modes use the same disk-refresh text template. The first sentence identifies
either `SAIV110 Surface Logger` or `OSU107 Instrument Logger`; all paragraphs are wrapped
to the terminal-width contract above.

The canonical unwrapped template is:

```text
Data logged by the {logger_name} is stored on its internal disk. When the device is connected to a PC, the disk normally appears automatically in File Explorer.

If logging continued while the device was connected to the PC, the latest log file may not be available for copying until the disk is refreshed.

Stop logging before refreshing the disk. Refreshing is blocked while logging is active.

After the refresh, the disk should reappear in File Explorer. You may need to select the COM port again unless your software does this automatically.

Refresh disk Y/N
```

`logger_name` is exactly `SAIV110 Surface Logger` in surface mode and
`OSU107 Instrument Logger` in instrument mode.

## New `usbDtrInfo` configuration

File: `config/system.ini`

The option exists separately in both logger sections:

```ini
[surface]
enable=1
folder=/surface
usbDtrInfo=both

[instrument0]
enable=0
usbDtrInfo=both
```

The generated INI comment is:

```ini
; usbDtrInfo: never=off, passive=only when not measuring/running, both=always.
```

Contract:

| Value | Meaning |
|---|---|
| `never` | Never emit the USB-open information message. |
| `passive` | Emit it only when the selected/dominant logger is not measuring or running. |
| `both` | Emit it on USB terminal open whether the logger is passive or active. This is the default. |

Additional rules:

- Values are parsed case-insensitively.
- Canonical output key: `usbDtrInfo`.
- Accepted input alias: `usb_dtr_info`.
- Missing keys use/migrate to the current default, `both`.
- Invalid values are rejected with one of these exact messages:
  - `surface.usbDtrInfo must be never, passive, or both`
  - `instrument0.usbDtrInfo must be never, passive, or both`
- If instrument mode is enabled, `[instrument0].usbDtrInfo` controls the behavior even if surface mode is also enabled. Otherwise `[surface].usbDtrInfo` is used.

The setting follows the same normal INI/update workflow as the other system settings. Existing software should retain its established `<U>` apply flow described in the previous handover.

## What triggers the information message

The message is emitted when the host opens the USB CDC serial connection and asserts the CDC DTR control state. No physical DTR conductor is required: the device USB connection only needs D+ and D-, because DTR is a virtual USB CDC control signal.

Software behavior:

- Open the serial port with DTR enabled/normal for the platform.
- A close/open cycle can produce one new message.
- Do not wait for this message as an acknowledgement; it can legally be absent because of `never`, `passive`, timing, or an older firmware version.
- Continue parsing measurement rows at all times.
- Normalize `CRLF`/`LF` line endings before matching text.
- Match stable prefixes and action strings, not a fixed count or fixed position of lines.
- Preserve unknown lines for forward compatibility instead of treating them as protocol errors.

## Exact USB-open output

Values below are examples; serial number, firmware version, device RTC date/time, voltage,
percentage, LED status, free space, and total space are dynamic.

### Instrument enabled, not measuring

```text
OSU107 Instrument logger SN107, Ver: 0.9.9M
Date/time: 2026-08-26 14:39:24
Battery: 10.75 V (62%)  Yellow led.
Free disk space: 5.918 MB of 7.965 MB

Hold <I> to wake instrument
```

After this message, OSU107 silently sends `G` to the connected CTD. If the CTD is already awake in a menu, the CTD may therefore present its menu after the information message. If the CTD is truly passive, `G` is ignored.

### Instrument enabled, measuring

```text
OSU107 Instrument logger SN107, Ver: 0.9.9M
Date/time: 2026-08-26 14:39:24
Battery: 10.35 V (36%)  Yellow led.
Free disk space: 5.922 MB of 7.965 MB

Type/hold <I> to stop instrument
N11 12:01:01 C00.000 T+24.099 P0001.07 OX028.79 OT000.02 OS000.45 Par4.47
```

The `N...` row illustrates that live instrument data may follow immediately. OSU107 never injects `G` while recent measurement data is active, so opening the terminal does not disturb a live instrument stream.

There is deliberately no `Instrument: Active` or `Instrument: Passive` line. The action line is the only instrument-specific status hint in this greeting:

- `Hold <I> to wake instrument`
- `Type/hold <I> to stop instrument`

### Surface enabled and running

```text
SAIV110 Surface logger SN107, Ver: 0.9.9M
Date/time: 2026-08-26 14:40:39
Battery: 10.35 V (36%)  Yellow led.
Free disk space: 5.922 MB of 7.965 MB
Surface-logger: Running

Type <I> for stop or <M> for menu
```

### Surface enabled and stopped

```text
SAIV110 Surface logger SN107, Ver: 0.9.9M
Date/time: 2026-08-26 14:40:39
Battery: 10.35 V (36%)  Yellow led.
Free disk space: 5.922 MB of 7.965 MB
Surface-logger: Stopped

Type <I> for start or <M> for menu
```

### Neither logger enabled

```text
OSU107 SN107, Ver: 0.9.9M
Date/time: 2026-08-26 14:40:39
Mode: Logger disabled
Battery: 10.35 V (36%)  Yellow led.
Free disk space: 5.922 MB of 7.965 MB
Type <CTRL+T> for OSU menu.
```

### Resource fallbacks and formatting

If a value cannot be read, the exact fallback is:

```text
Battery: n/a
Free disk space: n/a
```

When available:

- Battery voltage has two fractional digits.
- Disk values are binary MiB-sized values displayed as `MB` with three fractional digits.
- The disk line is `Free disk space: <free> MB of <total> MB`.

## Recommended parser behavior

Treat the greeting as a set of independent human-readable events. Suggested prefix matches:

| Prefix/exact text | Suggested software event |
|---|---|
| Prefix `OSU107 Instrument logger SN` | USB session information started in instrument mode; parse serial and version around `, Ver: `. |
| Prefix `SAIV110 Surface logger SN` | USB session information started in surface mode; parse serial and version around `, Ver: `. |
| Prefix `OSU107 SN` followed by `Mode: Logger disabled` | USB session information started with neither logger enabled. |
| `Date/time: ` | Parse the current OSU RTC value as `YYYY-MM-DD HH:MM:SS`; `n/a` means the RTC read failed. |
| `Mode: Logger disabled` | Neither logger is enabled. |
| `Battery: ` | Update displayed battery information. |
| `Free disk space: ` | Update displayed disk information. |
| `Surface-logger: Running` | Surface runtime state is running. |
| `Surface-logger: Stopped` | Surface runtime state is stopped. |
| `Hold <I> to wake instrument` | Present the passive instrument action. |
| `Type/hold <I> to stop instrument` | Present the active instrument action. |
| `Type <I> for stop or <M> for menu` | Present the running surface actions. |
| `Type <I> for start or <M> for menu` | Present the stopped surface actions. |

Important parser constraints:

- Do not assume the first serial bytes after opening are a greeting. Measurement data may already be arriving, especially with `usbDtrInfo=passive` or `never`.
- Do not discard `N...` or `S...` measurement rows while collecting greeting lines.
- Do not use the greeting as the sole source of persistent logger state; it is an informational snapshot.
- Do not infer that the CTD is passive merely because instrument mode is configured. The firmware intentionally removed that uncertain status claim.
- In `both` mode, the information lines and measurement stream share the same terminal channel and can be adjacent.

## Compatibility checklist

- Pre-`0.9.9K`: support legacy `[schedule]`, `/schedule`, and `SCH*` only when the detected firmware requires it.
- `0.9.9K` and later: generate `[surface]`, `/surface`, `SUR`, `SURSTART`, and `SURSTOP`.
- Expose `usbDtrInfo` as a three-choice field under both Surface and Instrument settings.
- Label choices as `Never`, `Passive only`, and `Both`, while writing lowercase wire values.
- Initialize newly created configurations to `both`.
- Keep instrument precedence if both logger modes are enabled.
- Keep all behavior from `HANDOVER_2026-08-20_SOFTWARE_INTEGRATION.md`, including semicolon storage defaults and configurable tilt fields.

## Release artifacts

These are the approved `0.9.9M` files currently packaged in the repository:

| Purpose | File | Bytes | SHA-256 |
|---|---|---:|---|
| J-Link/full flash | `tools/flashTool/hexfiles/program/zephyr.signed_0.9.9M.hex` | 1,642,994 | `CA03BDAD8E65B23550D230A70338B1FADE4EFB3934A194CE06660151F7DAD4D0` |
| Firmware update | `tools/flashTool/hexfiles/updateBin/osu_m_update_0.9.9M.bin` | 584,108 | `5087E2819DE522A8076E4B9777198B750D246846DA16B26FD16D828CFE6AC23E` |

The final firmware was built, flashed through J-Link, and verified on OSU107 SN107. USB/CTD behavior was tested through COM11; the J-Link probe used COM6/programmer ID `69650428`.

## Machine-readable summary

```json
{
  "handover_date": "2026-08-26",
  "firmware_version": "0.9.9M",
  "canonical_logger_name": "surface",
  "legacy_logger_name": "schedule",
  "terminology": {
    "ini_section": "surface",
    "legacy_ini_section": "schedule",
    "default_folder": "/surface",
    "legacy_default_folder": "/schedule",
    "menu_command": "SUR",
    "start_command": "SURSTART",
    "stop_command": "SURSTOP",
    "legacy_commands": ["SCH", "SCHSTART", "SCHSTOP"]
  },
  "usb_dtr_info": {
    "file": "config/system.ini",
    "sections": ["surface", "instrument0"],
    "canonical_key": "usbDtrInfo",
    "accepted_alias": "usb_dtr_info",
    "values": ["never", "passive", "both"],
    "default": "both",
    "case_insensitive": true,
    "instrument_dominates_when_both_enabled": true,
    "optional_message": true,
    "physical_dtr_wire_required": false
  },
  "storage_formats": {
    "values": ["full", "compact", "compact+DT"],
    "default": "compact+DT",
    "compact_datetime": {
      "canonical_value": "compact+DT",
      "applies_to": ["surface", "instrument0"],
      "final_fields": ["DATE", "TIME"],
      "date_format": "YYYY-MM-DD",
      "time_format": "HH:MM:SS",
      "unavailable_value": "n/a",
      "filename_suffix": "C",
      "live_output_changed": false
    }
  },
  "dtr_identity_lines": {
    "instrument": "OSU107 Instrument logger SN{serial}, Ver: {version}",
    "surface": "SAIV110 Surface logger SN{serial}, Ver: {version}",
    "disabled": "OSU107 SN{serial}, Ver: {version}",
    "date_time": "Date/time: {YYYY-MM-DD HH:MM:SS}"
  },
  "mode_identity": {
    "surface_only": "SAIV110",
    "instrument": "OSU107",
    "both_enabled": "OSU107",
    "terminal_max_columns": 72,
    "measurement_rows_wrapped": false,
    "surface_update_token": "SAIV110_UPDATE_CONFIG",
    "instrument_update_token": "OSU107_UPDATE_CONFIG"
  },
  "greeting_prefixes": [
    "OSU107 Instrument logger SN",
    "SAIV110 Surface logger SN",
    "OSU107 SN",
    "Date/time: ",
    "Mode: Logger disabled",
    "Battery: ",
    "Free disk space: ",
    "Surface-logger: "
  ],
  "instrument_action_lines": {
    "not_measuring": "Hold <I> to wake instrument",
    "measuring": "Type/hold <I> to stop instrument"
  },
  "surface_action_lines": {
    "running_status": "Surface-logger: Running",
    "running_action": "Type <I> for stop or <M> for menu",
    "stopped_status": "Surface-logger: Stopped",
    "stopped_action": "Type <I> for start or <M> for menu"
  },
  "forbidden_assumption": "Do not expect Instrument: Active or Instrument: Passive",
  "release_artifacts": {
    "hex": {
      "path": "tools/flashTool/hexfiles/program/zephyr.signed_0.9.9M.hex",
      "bytes": 1642994,
      "sha256": "CA03BDAD8E65B23550D230A70338B1FADE4EFB3934A194CE06660151F7DAD4D0"
    },
    "bin": {
      "path": "tools/flashTool/hexfiles/updateBin/osu_m_update_0.9.9M.bin",
      "bytes": 584108,
      "sha256": "5087E2819DE522A8076E4B9777198B750D246846DA16B26FD16D828CFE6AC23E"
    }
  }
}
```
