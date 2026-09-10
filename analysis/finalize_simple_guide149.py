"""Record the tested customer guide release and update the handover."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parent.parent
manifest = json.loads((R/'analysis/single_exe_149_manifest.json').read_text())
gui = json.loads((R/'analysis/runtime_test/guide149/gui_validation.json').read_text())
source = json.loads((R/'analysis/simple_guide149_validation.json').read_text())
digest = hashlib.sha256((R/manifest['output']).read_bytes()).hexdigest()
assert digest == manifest['sha256'] == gui['shipped_exe_sha256']
assert gui['full_formula_text_matches_source'] and len(gui['topics']) == 26
assert gui['single_exe_non_admin'] and not gui['instrument_commands_sent']
assert source['calculation_sources_unchanged']
old = json.loads((R/'analysis/single_exe_148_manifest.json').read_text())
assert hashlib.sha256((R/old['output']).read_bytes()).hexdigest() == old['sha256']
report = dict(release=manifest, gui=gui, source=source, previous_release_preserved=True)
(R/'analysis/simple_guide149_release_validation.json').write_text(json.dumps(report, indent=2))

p = R/'sd200DOc/PROSJEKTSTATUS.md'
s = p.read_text(encoding='utf-8')
s = s.replace('2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.8_Sept2026.exe**. Les [LES_MEG_System_Evaluation_148.md](../LES_MEG_System_Evaluation_148.md).',
              '2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.9_Sept2026.exe**. Les [LES_MEG_Simple_Guide_149.md](../LES_MEG_Simple_Guide_149.md).')
heading = '## Nyeste SIT-leveranse: 1.4.9 - enklere brukerguide, 10. september 2026'
if heading not in s:
    pos = s.index('## Nyeste SIT-leveranse: 1.4.8')
    section = heading + '''

Brukeren ba etter omstart om å fortsette med en enklere guide som handler om brukerens målinger og SIT-valg, uten omtale av hva som fantes i koden. Quick guide har nå 26 emner med betjening, praktiske metodevalg, enheter og korte eksempler. Temperatur og OSU107 er forenklet. Detaljert formeldokumentasjon er bevart utenfor guiden. Les [LES_MEG_Simple_Guide_149.md](../LES_MEG_Simple_Guide_149.md).

En-EXE bygget og alle 26 emner kontrollert i faktisk program: full tekst, tastatur, rulling, minimumsstørrelse og lukking. Konteksthjelpens emnemål er kontrollert. Beregningskilder og tidligere 1.4.8-EXE er uendret; runtime-kontroll inngår i bygget. Rapport: analysis/simple_guide149_release_validation.json. Ingen instrumentkommandoer, commit, push eller serverpublisering. Bygg: analysis/build_single_exe_149.py. Historisk kilde bevart i analysis/reference/sit_import_v148.

'''
    s = s[:pos] + section + s[pos:].replace('## Nyeste SIT-leveranse: 1.4.8', '## SIT-leveranse: 1.4.8', 1)
p.write_text(s, encoding='utf-8')
p = R/'AGENTS.md'
s = p.read_text(encoding='utf-8').replace('SAIV_Instrument_Terminal_v1.4.8_Sept2026.exe', 'SAIV_Instrument_Terminal_v1.4.9_Sept2026.exe')
s = s.replace('Les `LES_MEG_System_Evaluation_148.md` for enkel systemvurdering i guiden', 'Les `LES_MEG_Simple_Guide_149.md` for enklere brukerguide')
p.write_text(s, encoding='utf-8')
print('Validated SIT 1.4.9:', digest)
