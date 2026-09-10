from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parent.parent
manifest=json.loads((R/'analysis/single_exe_148_manifest.json').read_text())
gui=json.loads((R/'analysis/runtime_test/guide148/gui_validation.json').read_text())
numeric=json.loads((R/'analysis/system_evaluation148_validation.json').read_text())
digest=hashlib.sha256((R/manifest['output']).read_bytes()).hexdigest()
assert digest==manifest['sha256']==gui['shipped_exe_sha256']
assert gui['full_formula_text_matches_source'] and len(gui['topics'])==33
assert gui['single_exe_non_admin'] and not gui['instrument_commands_sent']
assert numeric['calculation_sources_unchanged'] and numeric['summary_words']<600
old=json.loads((R/'analysis/single_exe_147_manifest.json').read_text())
assert hashlib.sha256((R/old['output']).read_bytes()).hexdigest()==old['sha256']
guide=(R/'docs/SIT_CONVERSIONS_AND_FORMULAS.md').read_text(encoding='utf-8')
conductivity=guide.split('## Conductivity and salinity\n')[1].split('\n## ')[0]
assert 'SAIV' in conductivity.strip().split('\n\n')[-1] and 'STD' in conductivity.strip().split('\n\n')[-1]
report=dict(release=manifest,gui=gui,assessment=numeric,previous_release_preserved=True,
            conductivity_final_recommendation_preserved=True)
(R/'analysis/system_evaluation148_release_validation.json').write_text(json.dumps(report,indent=2))
p=R/'sd200DOc/PROSJEKTSTATUS.md';s=p.read_text(encoding='utf-8')
s=s.replace('2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.7_Sept2026.exe**. Les [LES_MEG_Conversion_Models_147.md](../LES_MEG_Conversion_Models_147.md).',
            '2. Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal_v1.4.8_Sept2026.exe**. Les [LES_MEG_System_Evaluation_148.md](../LES_MEG_System_Evaluation_148.md).')
heading='## Nyeste SIT-leveranse: 1.4.8 - systemvurdering, 10. september 2026'
if heading not in s:
    pos=s.index('## Nyeste SIT-leveranse: 1.4.7')
    section=heading+'''\n\nQuick guide har nå 33 emner. «System evaluation» gir en kort, enkel anbefaling; «System: measurement quality» forklarer kvalitet, fordeler og informasjonstap gjennom CTD/STD, SIT og OSU107. Start here viser til vurderingen. PSS-78/EOS-80/TEOS-10 og Steinhart-Hart, Kelvin-konstant og temperaturskala holdes tydelig fra hverandre. Les [LES_MEG_System_Evaluation_148.md](../LES_MEG_System_Evaluation_148.md).\n\nKildegrunnlaget omfatter den nye asmCTDdoc-rapporten og OSU107-handover-notatene. Ingen udokumentert tallfesting av OSU107-kanalnøyaktighet eller årstall for temperaturendring. Ingen målefil, sted eller installasjon oppgis i guiden. Formler og metodeidentifikator 1.4.7 er bevart; denne utgaven endrer hjelpetekst og programversjon.\n\nKontrollert: fire firmware/SIT-salinitetseksempler, 60 lydhastighetssammenligninger, uendrede beregningskilder og native runtime, samt alle 33 emner i faktisk en-EXE med full tekst, rulling, tastatur, lukking og kjøring uten administrator. Ingen instrumentkommandoer. Rapport: analysis/system_evaluation148_release_validation.json. Historisk 1.4.7-kilde er bevart i analysis/reference/sit_import_v147.\n\n'''
    s=s[:pos]+section+s[pos:].replace('## Nyeste SIT-leveranse: 1.4.7','## SIT-leveranse: 1.4.7',1)
p.write_text(s,encoding='utf-8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8')
s=s.replace('SAIV_Instrument_Terminal_v1.4.7_Sept2026.exe','SAIV_Instrument_Terminal_v1.4.8_Sept2026.exe')
s=s.replace('Les `LES_MEG_Conversion_Models_147.md` for formelguide og valg av beregningsmetoder.',
            'Les `LES_MEG_System_Evaluation_148.md` for enkel systemvurdering i guiden og `LES_MEG_Conversion_Models_147.md` for beregningsvalg.')
lines=s.splitlines(keepends=True)
for i,line in enumerate(lines):
    if line.startswith('Formelarbeidet er dokumentert'):
        lines[i]='Formelarbeidet er dokumentert i `sd200DOc/FORMELKARTLEGGING.md` og `sd200DOc/FORMELKONTROLL.md`. Native beregningsrutiner er bevart; Convert har eksplisitte metodevalg fra 1.4.7. Systemvurderingen i 1.4.8 forklarer kvalitet og gjenværende begrensninger.\n'
p.write_text(''.join(lines),encoding='utf-8')
print('Validated and recorded SIT 1.4.8:',digest)
