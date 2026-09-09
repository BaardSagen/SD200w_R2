"""Package the already-built and tested Studio executable; preserve older deliveries."""
from pathlib import Path
import hashlib,json,shutil,zipfile,subprocess
R=Path(__file__).resolve().parents[1];studio=R/'saiv-studio';exe=studio/'build/SAIVStudio.exe';digest=hashlib.sha256(exe.read_bytes()).hexdigest()
gui=json.loads((studio/'test-results/v030/gui_validation.json').read_text());assert gui['result']=='PASS' and gui['exe_sha256']==digest
tests=(studio/'build/Testing/Temporary/LastTest.log').read_text();assert all(s in tests for s in ('PASS 182 checks','PASS 50 compatibility checks','PASS 932 interval/clock'))
subprocess.run(['cmake','--install','build','--prefix','dist/SAIVStudio-0.3.0'],cwd=studio,check=True)
delivery=R/'SAIV_Studio_v0.3.0_Sept2026.exe'
if delivery.exists():assert hashlib.sha256(delivery.read_bytes()).hexdigest()==digest,'Do not overwrite an existing different delivery'
else:shutil.copy2(exe,delivery)
folder=studio/'dist/SAIVStudio-0.3.0';archive=studio/'dist/SAIVStudio-0.3.0-Windows-x64.zip'
if archive.exists():raise RuntimeError('Archive already exists; preserve the previous package')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(folder.rglob('*')):
  if p.is_file():z.write(p,Path(folder.name)/p.relative_to(folder))
report={'version':'0.3.0','date':'2026-09-10','exe':str(delivery.relative_to(R)),'sha256':digest,'size':delivery.stat().st_size,'archive':str(archive.relative_to(R)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'core_checks':182,'compatibility_checks':50,'settings_checks':932,'gui':gui,'physical_instrument_test':False,'native_platform':'Windows x64','default_save_format':'CSV','old_SD2_reading':True}
(R/'analysis/studio030_release_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
readme='''# SAIV Studio 0.3.0 – 10. september 2026

Kjør `SAIV_Studio_v0.3.0_Sept2026.exe`. Dette er et nytt, selvstendig Windows x64-program. Original SIT 1.4.3 og tidligere leveranser er beholdt.

Starter rett i terminalen med moderne utseende og Autodetect, Download, Convert, Merge, Interval, TIME/DATE, Print, Save og Setup. Skriv direkte i terminalen. Dialogtekst og målevisninger sender ikke tegn til instrumentet.

Nye målinger lagres som CSV med alle kolonner, tidsstempler og måleopplysninger. Eksisterende SD2 kan åpnes når RF2 og eventuelle OX2/OP2/SF2 følger med. Nye data trenger ikke SD2.

Convert/Merge bruker prosjektets SIT-moduler og dokumenterte SIT-formler. Målevisningen har tabell, parvise tidsgrafer/profiler, T-S og Multigraph. Dataverktøy lager et nytt datasett.

1164 automatiske kjerne-, kompatibilitets- og innstillingsprotokollkontroller består. GUI-testen kontrollerer direkte tegn/kontrolltegn, Setup-fokus, konvertering av 79 rader, Fahrenheit med original Celsius, CSV-lagring og grafer. Rapport: `analysis/studio030_release_validation.json`. Ingen fysisk instrumentport eller skriver ble brukt i denne testen.

Fysisk instrumentakseptanse av Studio gjenstår. Full funksjonslikhet med SIT, alle spesialeksporter, kalibrering/firmware, grafutskrift og Mac-/Linux-utgaver er ikke ferdige.

Kilde og bygg: `saiv-studio/`, kjør `build.cmd`. Program/lisenser/dokumentasjon i `saiv-studio/dist/SAIVStudio-0.3.0-Windows-x64.zip`. Detaljert funksjonsstatus: `saiv-studio/docs/FUNKSJONSSTATUS.md`.
'''
(R/'LES_MEG_SAIV_Studio_030.md').write_text(readme,encoding='utf-8')
p=R/'sd200DOc/PROSJEKTSTATUS.md';s=p.read_text(encoding='utf-8');s=s.replace('Oppdatert: 9. september 2026. Arbeidsmappe: `C:\\cprojects\\delphi`.','Oppdatert: 10. september 2026. Arbeidsmappe: `C:\\cproject\\delphi\\SD200w_R2`.');s=s.replace('Nyeste lokale leveranse er **SAIV_Instrument_Terminal','Nyeste lokale SIT-leveranse er **SAIV_Instrument_Terminal',1)
section='''## Ny selvstendig Studio-leveranse: 0.3.0, 10. september 2026

Brukeren ba om å lage Studio nå, med samme enkle terminalbetjening som SIT, men et moderne utseende. Brukeren presiserte at nye filer ikke trenger SD2; lesing av gamle SD2 skal beholdes. Aktivt Studio-arbeid er dermed gjenopptatt etter tidligere pause.

Leveranse: **SAIV_Studio_v0.3.0_Sept2026.exe**. Les [LES_MEG_SAIV_Studio_030.md](../LES_MEG_SAIV_Studio_030.md). Rett i terminal, enkel knapperekke, ekte UART 7E1, Convert/Merge, Interval/TIME-DATE, CSV som standard, gammel SD2-lesing, tabell/grafer og dataverktøy. Nytt grensesnitt kopierer ikke Windows 98-utseendet. Det er fortsatt en Windows x64-utgave; Linux/Mac er ikke levert.

Bygget med `saiv-studio/build.cmd`. 182 kjerne-, 50 kompatibilitets- og 932 innstillingsprotokollkontroller består. Samlet GUI-test og skjermbilder under `saiv-studio/test-results/v030`; SHA-bundet leveranserapport i `analysis/studio030_release_validation.json`. Fysisk instrumentakseptanse og full SIT-paritet gjenstår. Original SIT-kilde/moduler/leveranser er beholdt, og Studio 0.2.0-kilden er arkivert i `analysis/reference/saiv_studio_v020`. Ingen publisering eller push.

'''
marker='## Kjorende SIT gjennomgaatt';assert marker in s;s=s.replace(marker,section+marker,1);s=s.replace('Ingen ny Studio-utgave er bygget eller endret ennaa.','På dette tidspunktet var ingen ny Studio-utgave bygget; se den nyere 0.3.0-leveransen over.');p.write_text(s,encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='gui'},indent=2))
