"""Current GUI regression entry point; isolated transport, no COM ports."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("terminal_input_windows.py")),run_name="__main__")
