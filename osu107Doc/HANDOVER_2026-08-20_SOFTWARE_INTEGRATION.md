# OSU-107 firmware and software-integration handover 2026-08-20

This handover describes the user-visible and machine-visible changes delivered in
the firmware line from `0.9.9E` through the final `0.9.9J`. Commits `0.9.9G` through
`0.9.9J` were completed on 2026-08-20. The immediately preceding `0.9.9E` and
`0.9.9F` changes are included because they also change the PC application's serial
and configuration contract.

Use this document together with `OSUM_MULTI_INI_APP_SPEC.md`. The latter remains the
authoritative complete INI specification; this document is the delta and integration
checklist for the current release.

## Release baseline

- Firmware: `OSU-107 0.9.9J`
- Hardware target: `OSU-M rev 3.1.2`
- Firmware source commit: `d039fa6` (`Make tilt log presentation configurable`)
- Branch: `main`
- Hardware used for verification: OSU-107 `SN107` on `COM11`
- Programmer used for verification: J-Link probe `69650428` on `COM6`
- Final device state after testing: LT time base, default `Tilt/deg/1` presentation,
  instrument enabled, schedule disabled

The documentation commit containing this file is newer than the firmware source
commit above. No firmware behavior or binary is changed by the documentation commit.

## PC application: required changes at a glance

1. Parse the two new `Storage:` and `Sensors:` status lines in both schedule and
   instrument mode.
2. Treat serial receive data as a byte stream during CTD clock entry; typed clock
   characters can be echoed before a CR/LF is received.
3. Recognize the forwarded CTD passive transition and keep the port reader alive long
   enough to receive it after an idle menu.
4. Add/support the instrument-menu key `<Q>` named
   `Time & Date sync. to CTD.` and the Y/N synchronization flow.
5. Expose `prefix`, `unit`, and `frac_digits` under `[tilt]` in `lsm303.ini`.
6. Do not hard-code `Tilt`, `deg`, one decimal, ADC prefixes, or the storage separator
   when parsing new data files.
7. Use semicolon as the UI default for new schedule/instrument storage policies and
   two fractional digits as the UI default for new ADC channel definitions.
8. After editing files on the OSU disk, apply them with menu key `<U>` and wait for
   `OK OSU_107_UPDATE_CONFIG` before reporting success.

## 1. Logger status contract

Both schedule status and instrument status now contain these lines between free disk
space and battery status:

```text
Free disk space: 6.068 MB of 7.965 MB
Storage: Full, separator = ;
Sensors: Par(ch0), OxR(ch1)
Battery: 10.83 V (67%)  Yellow led.
```

Machine-readable grammar:

```text
Storage: <Format>, separator = <SeparatorDisplay>
Sensors: <Prefix>(ch<ChannelId>)[, <Prefix>(ch<ChannelId>)]*
```

Special values:

- Empty storage format is displayed as `Unknown`.
- Empty separator and one literal space are displayed as `space`.
- A tab separator is displayed as `tab`.
- Other separators, including `;` and `,`, are displayed literally.
- No enabled ADC channels is displayed as `Sensors: none`.

The values come from the active staged/NVS-backed configuration, not directly from
the host-visible files. Storage policy selection is deterministic:

1. Instrument storage is dominant when instrument and schedule are both enabled.
2. Otherwise the enabled logger owns the displayed storage policy.
3. If neither is enabled, the logger whose status was opened owns the display.

`Sensors:` lists every enabled ADC channel using its configured prefix and stored
channel ID. The application must not assume fixed names such as `Par` or `OxR`.

## 2. CTD terminal and menu behavior

### 2.1 Real-time clock character echo

When a user changes the CTD clock through CTD menu `<S>` and reaches:

```text
Set real-time clock
Format: YY-MM-DD-HH-MM-SS
```

OSU now forwards the CTD's unterminated character echo immediately. This is deliberately
limited to that interactive clock-input state. Measurement lines, status, range messages,
and menus remain normally line-buffered.

Application consequence: do not make all terminal rendering dependent on CR/LF. Append
incoming serial chunks as they arrive during interactive communication, while retaining a
separate line accumulator for parsers that require complete lines.

### 2.2 Automatic passive transition

If the CTD main menu is left idle, the CTD normally enters passive mode after about
60 seconds. OSU keeps the instrument receive path alive and forwards the final text:

```text
- passive -
Use Mag-Key or hold <I> to activate
```

Only after these lines are received does OSU release the menu-owned communication hold.
The hold is bounded at approximately 90 seconds if the instrument or cable disappears.

Application consequence:

- Treat either the exact `- passive -` line or the following wake prompt as a passive-state
  indication.
- Do not close or suspend the serial reader after only 60 seconds of menu inactivity.
- A 90-second upper wait bound is suitable for this specific transition.

### 2.3 OSU menu layout

The OSU options inserted above the CTD main menu use a common 25-character label width.
The current options are:

```text
OSU-107 option:
Copy data/ Refresh disk   <F>
Rinko Ox Adjust           <O>
Zero tilt level           <Z>
Verify calibration        <V>
Update config changes     <U>
Time & Date sync. to CTD. <Q>
```

The whitespace before the command token is presentation. Application logic should bind
to the stable `<F>`, `<O>`, `<Z>`, `<V>`, `<U>`, and `<Q>` tokens instead of counting
columns.

### 2.4 Synchronize OSU time and date from CTD

`<Q>` is available in the OSU option block shown with the CTD/instrument main menu. It is
not a schedule-logger command.

After the application or user sends `Q`, OSU displays exactly:

```text
For change date and time use CTD menu <S>
Continue date & time sync. Y/N
```

Cancel path:

- Send `N` (also accepted: `G` or ESC).
- OSU sends `G` internally and presents the CTD main menu again.

Continue path:

- Send `Y`.
- OSU sends CTD command `S`, reads and validates CTD date, time, and `LT`/`GMT`, then
  answers the CTD's `Change: Y/N` prompt with `N`.
- This internal CTD exchange and its intermediate menu are suppressed from the user port.
- OSU computes the weekday, sets the RV-3028, persists the matching LT/GMT flag, and
  immediately synchronizes the internal nRF clock.
- OSU then sends `G` internally and presents one clean CTD main menu.

Successful visible output uses a four-digit year and has this form:

```text
Setting date and time to "2026-08-20-16-17-43 LT"
Date & time in OSU is now synced to CTD time date = 2026-08-20-16-17-43 LT
```

`GMT` replaces `LT` when the CTD reports GMT. The second line above is the current exact
firmware text, including the phrase `time date`. For robust application behavior, match
the stable prefixes `Setting date and time to "` and
`Date & time in OSU is now synced to CTD` rather than matching the entire English sentence.

During the running synchronization, do not inject additional CTD menu keys. Treat the
success line or an `ERR:`/`WARNING:` line as the operation result, then wait for the final
menu.

## 3. Configuration and stored-data contract

### 3.1 Storage separator defaults

New schedule and instrument policies now default to:

```ini
separator=;
```

This default applies to both logger types. Explicit values already persisted in NVS are
preserved, including an intentionally empty separator representing spaces.

The separator changes stored data, not normal live CDC/UART presentation:

- Full storage joins the existing prefixed measurement tokens with the configured
  separator and does not add `FIELDS:`.
- Compact storage uses the same separator in `FIELDS:` and numeric data rows.
- Empty separator means the legacy space-separated form.

The application must read the logger-specific `separator` value from `system.ini` and
must not infer it from the current mode alone.

### 3.2 ADC channel decimal default

New ADC channel definitions now default to:

```ini
channel.0.fmt.frac_digits=2
```

The same rule applies to every newly created ADC channel. Existing explicit NVS values
are preserved. Valid ADC `fmt.frac_digits` values remain `0..6`.

### 3.3 Configurable tilt presentation

Tilt presentation is owned by `config/lsm303.ini`, section `[tilt]`:

```ini
[tilt]
enabled=1
prefix=Tilt
unit=deg
frac_digits=1
zero_mg_x=5.828857
zero_mg_y=1.274109
zero_mg_z=122.169495
```

The shown baseline values are only an example from the test unit. An application must
preserve the unit's actual `zero_mg_*` values when editing presentation fields.

Validation contract:

- `prefix` is required and is at most 24 bytes.
- `unit` may be empty and is at most 16 bytes.
- Neither field may contain whitespace, control characters, `=`, `;`, or `,`.
- `frac_digits` is an integer from `0` through `6`.
- Defaults are `prefix=Tilt`, `unit=deg`, and `frac_digits=1`.
- Older NVS/config content without the new fields is migrated/canonicalized with these
  compatible defaults.

Schedule and instrument mode use the same shared formatter and parser.

Full-format example with defaults:

```text
N00001 ... Tilt=1.2deg
S1 ... Tilt=1.2deg
```

Full token grammar:

```text
<prefix>=<fixed-point-value><unit>
```

Compact example with semicolon storage and enabled channels `Par`, `OxR`, and tilt:

```text
FIELDS: COUNT;Par;OxR;Tilt
1;4.41;0.29;1.2
```

In compact storage, the configured tilt `prefix` appears in `FIELDS:` and only the
fixed-point numeric value appears in the corresponding data column. The `unit` is not
written in compact rows.

Do not identify tilt by searching only for the literal strings `Tilt` or `deg`. Use the
current `[tilt]` configuration, or the compact `FIELDS:` metadata, as the schema.

## 4. Applying edits made by the PC application

Editing files on the exposed OSU disk does not automatically change runtime/NVS state.
The normal end-user path is the OSU menu option:

```text
Update config changes     <U>
```

`<U>` performs the equivalent of `CFG -> MIR` followed by `CFG -> APPLY` and reports:

```text
OSU-107 UPDATE_CONFIG start: MIR + APPLY
OK OSU_107_UPDATE_CONFIG
```

Application workflow:

1. Read the complete existing INI file.
2. Change only fields owned by the application and preserve calibration/identity fields.
3. Safely finish the disk write and allow the OSU to regain filesystem ownership.
4. Reconnect/select the COM port if the disk-refresh flow requested it.
5. Open the relevant OSU menu and send `U`.
6. Wait for `OK OSU_107_UPDATE_CONFIG` before declaring success.
7. Treat `ERR OSU_107_UPDATE_CONFIG ...` as failure. Firmware may rebuild `/config`
   from NVS after a failed MIR/APPLY; in that case the attempted disk edits were not applied.

The hidden-menu `CFG -> MIR` and `CFG -> APPLY` commands remain available for service and
diagnostic use, but an ordinary PC UI should prefer `<U>`.

## 5. Compatibility recommendations

- Detect firmware version from the `Ver:` line. Enable the complete contract in this
  document for `0.9.9J` and later.
- Keep unknown status/menu lines visible and ignore them gracefully; do not parse status
  by fixed line number.
- Normalize `CRLF`, `LFCR`, and single CR/LF for line-oriented parsing. The firmware and
  legacy CTD do not use one line-ending order everywhere.
- Keep serial rendering and semantic parsing separate. Rendering must accept fragments;
  semantic parsers can consume completed normalized lines.
- Treat menu labels as presentation and command tokens such as `<Q>` as control identity.
- Read configuration before parsing stored full-format rows because prefix and unit are
  user-configurable.
- Prefer compact `FIELDS:` as the authoritative column schema for compact files.

## 6. Hardware verification completed

The following behavior was exercised on SN107:

- Schedule and instrument status showed the active storage format, separator, and enabled
  sensor prefixes/channel IDs.
- All 17 CTD date/time-entry characters echoed through OSU before a terminating line break.
- Leaving the CTD menu idle forwarded both passive lines after the CTD timeout.
- Clock synchronization covered cancel, LT, GMT, hidden internal exchange, one final menu,
  and OSU/CTD readback.
- Custom tilt configuration `prefix=Incl`, `unit=degree`, `frac_digits=3` produced
  `Incl=1.170degree` in instrument full output.
- The same custom configuration produced
  `FIELDS: COUNT;Par;OxR;Incl` and numeric `...;1.936` rows in schedule compact storage.
- The exact final `0.9.9J` binary was flashed and produced default output such as
  `Tilt=1.2deg`.

## 7. Firmware artifacts

Program HEX:

```text
tools/flashTool/hexfiles/program/zephyr.signed_0.9.9J.hex
SHA-256: C427464A08AEA9E7E559BD89D566F0041EFD928A6056397A393B8E7ED62C7922
```

File-update BIN:

```text
tools/flashTool/hexfiles/updateBin/osu_m_update_0.9.9J.bin
SHA-256: 59348E80C096214CB0891344762322A9D0CCD1428D339E00AC4CA36A1D3F220A
```

The packaged files match the artifacts used for final verification.

## 8. Relevant commit map

- `054b93b` - status storage/sensor details (`0.9.9E`)
- `689aa03` - CTD clock-entry echo (`0.9.9F`)
- `58b56a1` - passive timeout forwarding (`0.9.9G`)
- `8c4de9e` - CTD-to-OSU clock synchronization (`0.9.9H`)
- `3f6ec0c` - menu wording/alignment and new defaults (`0.9.9I`)
- `d039fa6` - configurable shared tilt presentation (`0.9.9J`)

## 9. Compact machine-readable delta

This JSON is a summary for importing into an application-development task. The prose
above remains authoritative when more detail is required.

```json
{
  "firmware": "0.9.9J",
  "hardware": "OSU-M rev 3.1.2",
  "status": {
    "new_line_prefixes": ["Storage: ", "Sensors: "],
    "separator_aliases": [
      {"stored": "", "display": "space"},
      {"stored": " ", "display": "space"},
      {"stored": "\\t", "display": "tab"}
    ],
    "storage_precedence_when_both_enabled": "instrument"
  },
  "terminal": {
    "clock_entry_echo_may_be_unterminated": true,
    "passive_lines": [
      "- passive -",
      "Use Mag-Key or hold <I> to activate"
    ],
    "passive_receive_hold_max_seconds": 90
  },
  "clock_sync": {
    "menu_key": "Q",
    "menu_label": "Time & Date sync. to CTD.",
    "answers": ["Y", "N"],
    "success_prefix": "Date & time in OSU is now synced to CTD",
    "timestamp_format": "YYYY-MM-DD-HH-MM-SS LT|GMT"
  },
  "defaults": {
    "schedule_separator": ";",
    "instrument_separator": ";",
    "adc_frac_digits": 2,
    "tilt_prefix": "Tilt",
    "tilt_unit": "deg",
    "tilt_frac_digits": 1
  },
  "tilt_config": {
    "file": "config/lsm303.ini",
    "section": "tilt",
    "fields": ["prefix", "unit", "frac_digits"],
    "full_token": "<prefix>=<value><unit>",
    "compact_field": "<prefix>",
    "frac_digits_range": [0, 6]
  },
  "apply": {
    "menu_key": "U",
    "success_line": "OK OSU_107_UPDATE_CONFIG"
  }
}
```
