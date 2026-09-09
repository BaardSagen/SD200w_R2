from pathlib import Path
import hashlib,json,shutil,zipfile,subprocess
r=Path(__file__).resolve().parents[1];studio=r/'saiv-studio'
test=json.loads((studio/'test-results/v031/startup_validation.json').read_text());exe=studio/'build/SAIVStudio.exe';digest=hashlib.sha256(exe.read_bytes()).hexdigest()
assert test['result']=='PASS' and test['exe_sha256']==digest
log=(studio/'build/Testing/Temporary/LastTest.log').read_text();assert all(s in log for s in ['PASS 182 checks','PASS 50 compatibility checks','PASS 932 interval/clock'])
for name in ['README.md','docs/FUNKSJONSSTATUS.md','docs/KOMMUNIKASJON.md']:
 p=studio/name;s=p.read_text(encoding='utf-8').replace('0.3.0','0.3.1');p.write_text(s,encoding='utf-8')
p=studio/'README.md';s=p.read_text(encoding='utf-8');lines=s.splitlines();lines[2:2]=['0.3.1 retter en oppstartsfeil som presset terminalen sammen når ingen målefil var åpen. Vanlig oppstart uten demo er kontrollert i tre vindusstørrelser. Regresjonstest: `analysis/test_studio_startup031.py`.',''];p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
note='''# SAIV Studio 0.3.1 – rettet oppstartsvisning

Kjør `SAIV_Studio_v0.3.1_Sept2026.exe`.

0.3.0 presset terminalen sammen til en smal stripe ved vanlig oppstart uten måledata. En ubetinget SameLine før valgfrie overskriftsknapper flyttet også arbeidsområdet til høyre. SameLine brukes nå bare når en knapp faktisk skal vises.

Feilen er gjenskapt i bevart 0.3.0. 0.3.1 er åpnet normalt uten demodata eller testtransport og visuelt kontrollert ved 1180×780, 920×600 og 1450×900. Terminalfeltet fyller nå venstresiden. Demovisning er også kontrollert. Alle tre CTest-grupper består (182 + 50 + 932 kontroller).

Ingen instrumentport er åpnet under testen. Endringen gjelder oppstartsoppsett og versjonsmerking. Øvrig funksjonsstatus og begrensninger står i `saiv-studio/docs/FUNKSJONSSTATUS.md`.

Tidligere EXE/ZIP og 0.3.0-kilde er beholdt. Kildearkiv: `analysis/reference/saiv_studio_v030`. Bygg: `saiv-studio/build.cmd`. Skjermbilder og regresjonsrapport: `saiv-studio/test-results/v031`.
'''
(r/'LES_MEG_SAIV_Studio_031.md').write_text(note,encoding='utf-8')
p=r/'sd200DOc/PROSJEKTSTATUS.md';s=p.read_text(encoding='utf-8');marker='## Ny selvstendig Studio-leveranse: 0.3.0, 10. september 2026';assert marker in s
section='''## Rettet Studio-leveranse: 0.3.1, 10. september 2026

Brukerens skjermbilde viste at vanlig oppstart uten måledata presset terminalen til høyre. Årsaken var ubetinget SameLine før valgfrie knapper. 0.3.1 retter dette. Tidligere test med demodata skjulte feilen.

Leveranse: **SAIV_Studio_v0.3.1_Sept2026.exe**. Les [LES_MEG_SAIV_Studio_031.md](../LES_MEG_SAIV_Studio_031.md). Normal oppstart uten demo/testtransport kontrollert visuelt og med måling av terminalbredden i tre vindusstørrelser, pluss demo-regresjon. Alle 1164 CTest-kontroller består. Ingen fysisk instrumentport brukt. Rapport: `analysis/studio031_release_validation.json`; skjermbilder: `saiv-studio/test-results/v031`. 0.3.0-kilden er bevart i `analysis/reference/saiv_studio_v030`, og tidligere leveranser er beholdt.

'''
s=s.replace(marker,section+marker,1);p.write_text(s,encoding='utf-8')
subprocess.run(['cmake','--install','build','--prefix','dist/SAIVStudio-0.3.1'],cwd=studio,check=True)
delivery=r/'SAIV_Studio_v0.3.1_Sept2026.exe';assert not delivery.exists();shutil.copy2(exe,delivery)
folder=studio/'dist/SAIVStudio-0.3.1';archive=studio/'dist/SAIVStudio-0.3.1-Windows-x64.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(folder.rglob('*')):
  if p.is_file():z.write(p,Path(folder.name)/p.relative_to(folder))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and hashlib.sha256(z.read(folder.name+'/SAIVStudio.exe')).hexdigest()==digest
report=dict(version='0.3.1',exe=delivery.name,sha256=digest,archive=str(archive.relative_to(r)),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),startup=test,ctest_checks=1164,zip_and_executable_verification='PASS',physical_instrument_test=False)
(r/'analysis/studio031_release_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'exe':delivery.name,'sha256':digest,'checks':'PASS'},indent=2))
