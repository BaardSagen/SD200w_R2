"""Package the verified SIT release for manual server upload."""
from pathlib import Path
import hashlib, json, zipfile
import pefile

root = Path(__file__).resolve().parent.parent
folder = root/'update_server'
exe = root/'SAIV_Instrument_Terminal_v1.4.11_Sept2026.exe'
notes = folder/'readme_v1.4.11.txt'
archive = folder/(exe.stem.lower()+'.zip')
m = json.loads((root/'analysis/single_exe_1411_manifest.json').read_text())
validation = json.loads((root/'analysis/firmware1411_validation.json').read_text())
acceptance = validation['physical']['full_cycle_acceptance']
assert acceptance['passed'] and acceptance['success_dialog_seen']
digest = hashlib.sha256(exe.read_bytes()).hexdigest()
assert digest == m['sha256'] == validation['build']['sha256']
if digest != acceptance['build_sha256']:
    notes_check = validation['customer_notes_check']
    assert notes_check['passed'] and notes_check['build_sha256'] == digest
    full = json.loads((root/acceptance['report']).read_text())
    checked = json.loads((root/notes_check['report']).read_text())
    assert full['passed'] and checked['passed']
    assert full['build']['runtime_sha256'] == checked['build']['runtime_sha256'] == m['runtime_sha256']
pe = pefile.PE(str(exe)); v = pe.VS_FIXEDFILEINFO[0]
assert (v.FileVersionMS, v.FileVersionLS) == (0x10004, 0xb0000)
notices = 'MINIZ\n\n' + (root/'sit_update/miniz/LICENSE').read_text(encoding='utf-8')
notices += '\n\nGSW-C\n\n' + (root/'sit_import/vendor/gsw/LICENSE').read_text(encoding='utf-8')
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(exe, exe.name)
    z.write(notes, 'README.txt')
    z.writestr('THIRD_PARTY_NOTICES.txt', notices.encode('utf-8'))
public = dict(version='1.4.11', url='https://saiv.no/software/'+archive.name,
              readme_url='https://saiv.no/software/'+notes.name,
              sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.read(exe.name) == exe.read_bytes()
    assert z.read('README.txt') == notes.read_bytes()
    assert z.read('THIRD_PARTY_NOTICES.txt') == notices.encode('utf-8')
assert archive.stat().st_size < 100*1024*1024
old = folder/'latest.json'
previous = json.loads(old.read_text(encoding='utf-8'))
if previous['version'] != public['version']:
    backup = folder/('latest_v'+previous['version']+'.json')
    if backup.exists():
        assert backup.read_bytes() == old.read_bytes()
    else:
        backup.write_bytes(old.read_bytes())
old.write_text(json.dumps(public, indent=2)+'\n', encoding='utf-8')
(root/'analysis/update_server1411_validation.json').write_text(json.dumps(
    dict(manifest=public, exe_sha256=digest, zip_bytes=archive.stat().st_size,
         crc_and_contents_checked=True, embedded_version_checked=True,
         included_licences=['miniz','GSW-C']), indent=2))
print(json.dumps(public, indent=2))
print('ZIP bytes:', archive.stat().st_size)
