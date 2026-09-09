"""Authorized COM7 bench helper: native menu navigation, then H/passive.
Only use with an instrument whose active testing is authorized.
Every TX/RX is retained by probe_com7_native_wake.py, even on failure.
"""
from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(root/'analysis/probe_com7_native_wake.py'),'--passive'],cwd=root,check=True)
report=json.loads((root/'analysis/com7_native_wake_probe.json').read_text())
assert report['final_phase']=='passive',report['final_phase']
(root/'analysis/com7_native_passive_preparation.json').write_text(json.dumps(report,indent=2))
