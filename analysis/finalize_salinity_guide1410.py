"""Validate and record the salinity terminology help release."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parent.parent
m = json.loads((R/'analysis/single_exe_1410_manifest.json').read_text())
g = json.loads((R/'analysis/runtime_test/guide1410/gui_validation.json').read_text())
s = json.loads((R/'analysis/salinity_guide1410_validation.json').read_text())
assert hashlib.sha256((R/m['output']).read_bytes()).hexdigest() == m['sha256'] == g['shipped_exe_sha256']
assert len(g['topics']) == 26 and g['full_formula_text_matches_source']
assert g['single_exe_non_admin'] and not g['instrument_commands_sent']
assert s['calculation_sources_unchanged'] and s['salinity_text_checked']
(R/'analysis/salinity_guide1410_release_validation.json').write_text(json.dumps(dict(release=m, gui=g, source=s), indent=2))
p = R/'sd200DOc/PROSJEKTSTATUS.md'
text = p.read_text(encoding='utf-8')
text = text.replace('2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.9_Sept2026.exe**. Les [LES_MEG_Simple_Guide_149.md](../LES_MEG_Simple_Guide_149.md).', '2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.10_Sept2026.exe**. Les [LES_MEG_Salinity_Guide_1410.md](../LES_MEG_Salinity_Guide_1410.md).')
heading = '## Nyeste SIT-leveranse: 1.4.10 - S og instrumentets salinitetsmetode, 10. september 2026'
if heading not in text:
    pos = text.index('## Nyeste SIT-leveranse: 1.4.9')
    section = heading + '''

Brukeren ba om å rette salinitetsforklaringen i selve programmet. Quick guide sier nå uttrykkelig at SD208 beregner S fra C/T/P med PSS-78. S brukes i symbolforklaringer og eksempler; SP forklares én gang som fagbetegnelse for samme praktiske salinitet. Instrumentets lagrede S skilles fra ny beregning i Convert, og guiden forklarer at Convert ikke endrer instrumentets metode. Les [LES_MEG_Salinity_Guide_1410.md](../LES_MEG_Salinity_Guide_1410.md).

En-EXE bygget og alle 26 guideemner kontrollert i faktisk program, inkludert full tekst, tastatur, rulling og lukking. Kun guide og programversjon endret. Tidligere 1.4.9-EXE og kilde bevart i analysis/reference/sit_import_v149. Bygg: analysis/build_single_exe_1410.py. Rapport: analysis/salinity_guide1410_release_validation.json. Ingen instrumentkommandoer, commit, push eller serverpublisering.

'''
    text = text[:pos] + section + text[pos:].replace('## Nyeste SIT-leveranse: 1.4.9', '## SIT-leveranse: 1.4.9', 1)
p.write_text(text, encoding='utf-8')
p = R/'AGENTS.md'
text = p.read_text(encoding='utf-8').replace('SAIV_Instrument_Terminal_v1.4.9_Sept2026.exe', 'SAIV_Instrument_Terminal_v1.4.10_Sept2026.exe')
text = text.replace('`LES_MEG_Simple_Guide_149.md` for enklere brukerguide', '`LES_MEG_Salinity_Guide_1410.md` for salinitetsforklaring i brukerguiden')
p.write_text(text, encoding='utf-8')
print('Validated SIT 1.4.10:', m['sha256'])
