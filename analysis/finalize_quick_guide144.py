from pathlib import Path
import hashlib,json,pefile
R=Path(__file__).resolve().parent.parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((R/'analysis/single_exe_144_manifest.json').read_text())
old=json.loads((R/'analysis/single_exe_143_manifest.json').read_text())
assert sha(R/m['output'])==m['sha256']
assert sha(R/old['output'])==old['sha256']
assert m['helper_sha256']==old['helper_sha256']
archive=R/'analysis/reference/sit_import_v143'
changed=[p.name for p in archive.iterdir() if p.is_file() and p.read_bytes()!=(R/'sit_import'/p.name).read_bytes()]
assert changed==['update_ui.inc'],changed
gui=json.loads((R/'analysis/runtime_test/guide144/gui_validation.json').read_text())
assert len(gui['topics'])==9 and gui['update_dialog_preserved_without_network']
assert gui['arrow_navigation'] and gui['escape_restores_main']
assert gui['close_button_and_reopen'] and gui['window_close'] and gui['minimum_size_text_accessible']
module=pefile.PE(str(R/'SIT_Import144.dll'))
deps=[i.dll.decode() for i in module.DIRECTORY_ENTRY_IMPORT]
assert not any('libgcc' in x.lower() or 'libstdc' in x.lower() or 'libwinpthread' in x.lower() for x in deps)
report=dict(output=m['output'],sha256=m['sha256'],previous_release_preserved=True,
            instrument_and_data_sources_unchanged=True,installer_helper_unchanged=True,
            runtime_changes='Version/About resources, DLL names and PE checksum only (build assertion)',
            module_dependencies=deps,gui=gui,visual_review='start.png, topic_4.png and minimum_size.png inspected',
            physical_instrument_test=False,visual_instrument_walkthrough='Deferred as requested')
(R/'analysis/guide144_release_validation.json').write_text(json.dumps(report,indent=2))
p=R/'sd200DOc/PROSJEKTSTATUS.md';s=p.read_text(encoding='utf-8')
s=s.replace('Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.3_Sept2026.exe**','Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.4_Sept2026.exe**',1)
anchor='## Rettet Studio-leveranse: 0.3.1, 10. september 2026'
section='''## Nyeste SIT-leveranse: 1.4.4 – Quick guide, 10. september 2026

Brukeren ba om en Quick guide også i original SIT, tilpasset SITs egne menyer og utseende. Help > Quick guide har nå ni korte engelske emner i et vanlig SIT-hjelpevindu, med emnevalg, tastaturbetjening og justerbar størrelse. Guiden fungerer offline og uten instrument. Les [LES_MEG_Quick_Guide_144.md](../LES_MEG_Quick_Guide_144.md).

Leveranse: **SAIV_Instrument_Terminal_v1.4.4_Sept2026.exe** (én EXE). Faktisk GUI-kontroll av alle emner, piltaster, Esc/Close/vinduskryss, gjenåpning, minimumsstørrelse og bevart Update software-meny bestått. Bilder kontrollert visuelt. Rapport: `analysis/guide144_release_validation.json`. Ingen instrumentkommandoer eller nettverkskall i testen. Instrument- og datakilder samt installerhjelperen er bevart; runtime har bare nye versjonsressurser/DLL-navn/sjekksum. Bygg: `analysis/build_single_exe_144.py`. 1.4.3-kilden er arkivert i `analysis/reference/sit_import_v143`, og det historiske bygget bruker arkivet. Tidligere EXE-er beholdt. Ingen publisering eller push.

Brukeren har ikke instrument tilgjengelig nå. En visuell gjennomgang av faktisk SIT-bruk er mulig, men skal **ikke lages før instrumentene er tilkoblet**. Kun tekstguiden er levert nå.

'''
assert anchor in s
assert '## Nyeste SIT-leveranse: 1.4.4' not in s
s=s.replace(anchor,section+anchor,1)
s=s.replace('## Siste lokale leveranse: 1.4.3 -','## Tidligere lokal leveranse: 1.4.3 -',1)
p.write_text(s,encoding='utf-8')
print(json.dumps({'output':m['output'],'sha256':m['sha256'],'validation':'passed'},indent=2))
