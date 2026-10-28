"""Package the verified hardware-channel release for manual server upload."""
from pathlib import Path
import hashlib
import json
import zipfile
import pefile

root = Path(__file__).resolve().parent.parent
folder = root / 'update_server'
exe = root / 'SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe'
notes = folder / 'readme_v1.4.12.txt'
archive = folder / (exe.stem.lower() + '.zip')
# Existing clients derive the exact, case-sensitive EXE entry from the ZIP URL.
program_entry = archive.with_suffix('.exe').name
manifest = json.loads((root / 'analysis/single_exe_1412_manifest.json').read_text())
release = json.loads((root / 'analysis/firmware1412_final_release_validation.json').read_text())
static = json.loads((root / 'analysis/firmware1412_final_static_validation.json').read_text())
digest = hashlib.sha256(exe.read_bytes()).hexdigest()
assert release['passed'] and static['passed']
assert digest == manifest['sha256'] == release['build']['sha256'] == static['build']['sha256']
assert release['exports_byte_identical_to_1411'] and release['source_files_unchanged']
assert release['live_server_both_channels_passed'] and release['cross_hardware_rejected']
assert static['embedded_components_exact']
pe = pefile.PE(str(exe))
version = pe.VS_FIXEDFILEINFO[0]
assert (version.FileVersionMS, version.FileVersionLS) == (0x10004, 0xc0000)
assert (version.ProductVersionMS, version.ProductVersionLS) == (0x10004, 0xc0000)
unsigned = pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].Size == 0
assert unsigned, 'Signed release requires updated release validation and notes.'
notices = 'MINIZ\n\n' + (root / 'sit_update/miniz/LICENSE').read_text(encoding='utf-8')
notices += '\n\nGSW-C\n\n' + (root / 'sit_import/vendor/gsw/LICENSE').read_text(encoding='utf-8')
for text in (notes.read_text(encoding='utf-8'), notices):
    for forbidden in ('ctrl+t', 'ctrl + t', 'service menu', 'servicemeny', 'fwust', 'osu_m_update.bin'):
        assert forbidden not in text.lower(), forbidden

# Fixed metadata makes repeated packaging byte-identical.
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name, data in ((program_entry, exe.read_bytes()), ('README.txt', notes.read_bytes()),
                       ('THIRD_PARTY_NOTICES.txt', notices.encode('utf-8'))):
        info = zipfile.ZipInfo(name, date_time=(2026, 10, 28, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        z.writestr(info, data, compresslevel=9)
public = dict(version='1.4.12', url='https://saiv.no/software/' + archive.name,
              readme_url='https://saiv.no/software/' + notes.name,
              sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.namelist() == [program_entry, 'README.txt', 'THIRD_PARTY_NOTICES.txt']
    expected_entry = public['url'].rsplit('/', 1)[1][:-4] + '.exe'
    assert program_entry == expected_entry
    assert z.read(expected_entry) == exe.read_bytes()
    assert z.read('README.txt') == notes.read_bytes()
    assert z.read('THIRD_PARTY_NOTICES.txt') == notices.encode('utf-8')
assert archive.stat().st_size < 100 * 1024 * 1024
latest = folder / 'latest.json'
latest.write_text(json.dumps(public, indent=2) + '\n', encoding='utf-8')
report = dict(manifest=public, exe_sha256=digest, zip_bytes=archive.stat().st_size,
              updater_expected_program=program_entry, updater_exact_name_checked=True,
              crc_and_contents_checked=True, embedded_version_checked=True,
              customer_text_checked=True, included_licences=['miniz', 'GSW-C'],
              unsigned=unsigned, release_validation='analysis/firmware1412_final_release_validation.json',
              server_uploaded=False, installer_executed=False)
(root / 'analysis/update_server1412_validation.json').write_text(
    json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
