"""Bounded native SD2 interoperability probe, NOT a production converter.

Creates a fresh test directory, preserves input verbatim, and writes a standard
CTD projection for the existing Delphi reader. Extra fields are NOT yet wired to
native graphs. Deliberately rejects data this probe cannot represent exactly.
"""
from pathlib import Path
import csv, hashlib, json, re, struct, time
from datetime import datetime
from recovered_formulas import salinity

ROOT = Path(__file__).resolve().parent.parent

def build(source, destination):
    raw = source.read_bytes()
    lines = raw.decode('utf-8-sig').splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith('FIELDS:'))
    fields = lines[start].split(':', 1)[1].strip().split(';')
    assert not any(f.startswith(('M1_', 'M2_')) for f in fields), 'Merge is out of scope'
    rows = list(csv.DictReader(lines[start + 1:], fieldnames=fields, delimiter=';'))
    assert rows and all(all(row.get(f) for f in ('C', 'T', 'P', 'DATE', 'TIME', 'Sound_velocity_SIT_m_s')) for row in rows)
    dates = [datetime.fromisoformat(row['DATE'] + 'T' + row['TIME']) for row in rows]
    assert all(d.microsecond == 0 and 2000 <= d.year <= 2079 for d in dates), 'Probe requires whole seconds and verified year range'
    header_text = '\n'.join(lines[:start])
    serial = re.search(r'Ser No (\d+)', header_text)
    air = re.search(r'\bAP([\d.]+)', header_text)
    assert serial and air, 'Probe requires CTD serial and air pressure'
    # Native header: version short, instrument int, channel flags int,
    # instrument mode byte, a format marker byte, revision short, reserved.
    # Same mode and revision as the existing native CTDOF fixture.
    optical = 'OF' in fields
    assert not optical or all(row['OF'] for row in rows)
    flags = 0x1f | (0x100 if optical else 0)
    head = struct.pack('<HiIBBH', 12, int(serial[1]), flags, 5, 1, 12).ljust(52, b'\0')
    records, optics, expected = [], [], []
    for row, dt in zip(rows, dates):
        c, t, p = (float(row[f]) for f in ('C', 'T', 'P'))
        s = float(row['S']) if row.get('S') else salinity(c, t, p)
        v = float(row['Sound_velocity_SIT_m_s'])
        number = int(row['COUNT'])
        stamp = (dt.year % 100, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        records.append(struct.pack('<6BHI5d', *stamp, 0, number, s, c, t, p, v))
        if optical:
            optics.append(struct.pack('<2f', float(row['OF']), 0))
        expected.append([s, c, t, p, v])
    first = dates[0]
    reference = struct.pack('<II6BHf4dhhdd', 1, 1, first.year % 100,
        first.month, first.day, first.hour, first.minute, first.second, 2,
        float(air[1]) * 760 / 1013.25, *([-999.] * 4), -2, 0, 35., 0.)
    destination.mkdir(parents=True, exist_ok=False)
    target = destination / 'convert_probe.SD2'
    target.write_bytes(head + b''.join(records))
    target.with_suffix('.RF2').write_bytes(reference)
    if optical:
        target.with_suffix('.OP2').write_bytes(b''.join(optics))
    (destination / 'all_fields_original.txt').write_bytes(raw)
    report = dict(prototype_only=True, source=str(source),
        source_sha256=hashlib.sha256(raw).hexdigest(), rows=len(rows),
        fields=fields, native_expected=expected, target=str(target),
        notes=['Extra fields preserved in original text; native display integration remains pending.',
               'S computed for native CTD projection using previously verified recovered routine.',
               'No general SD2 writer or missing-value policy is asserted by this probe.'])
    (destination / 'projection.json').write_text(json.dumps(report, indent=2))
    return report

if __name__ == '__main__':
    source = next((ROOT / 'analysis/runtime_test/fahrenheit135').glob('celsius_*.txt'))
    report = build(source, ROOT / 'analysis/runtime_test/native_convert' / str(time.time_ns()))
    print(report['target'])
