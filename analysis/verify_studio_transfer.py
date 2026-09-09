from pathlib import Path
import zipfile,subprocess,time,json
R=Path(__file__).resolve().parent.parent;S=R/'saiv-studio';dest=S/('transfer-check-'+str(time.time_ns()));dest.mkdir()
with zipfile.ZipFile(S/'releases/SAIVStudio_0.1.0_Source.zip') as z:
 for name in z.namelist():assert (dest/name).resolve().is_relative_to(dest.resolve())
 z.extractall(dest)
result=subprocess.run(['cmd.exe','/d','/c',str(dest/'build.cmd')],cwd=dest,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(R/'analysis/studio_transfer_build.log').write_text(result.stdout,encoding='utf-8')
report={'result':'PASS' if result.returncode==0 else 'FAIL','source_archive':'saiv-studio/releases/SAIVStudio_0.1.0_Source.zip','extracted_to':str(dest),'returncode':result.returncode,'uses_original_delphi_exe':False}
(R/'analysis/studio_transfer_validation.json').write_text(json.dumps(report,indent=2));print(result.stdout[-4000:]);print(json.dumps(report,indent=2));raise SystemExit(result.returncode)
