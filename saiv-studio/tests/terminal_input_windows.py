"""Run the current Studio GUI test from the complete project checkout."""
from pathlib import Path
import runpy
script=Path(__file__).resolve().parents[2]/'analysis/test_studio_gui030.py'
if not script.is_file():
    raise SystemExit('GUI verification requires the complete project checkout, including analysis/. Core tests run with build.cmd.')
runpy.run_path(str(script),run_name='__main__')
