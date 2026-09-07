"""Check transferred files and executable hashes without starting an instrument."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parent.parent
inventory = json.loads((root / "analysis/transfer_inventory.json").read_text(encoding="utf-8"))
errors = []
for name in inventory["files"]:
    if not (root / name).is_file():
        errors.append(f"Missing: {name}")
for name, expected in inventory["executable_sha256"].items():
    path = root / name
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append(f"SHA-256 mismatch: {name}")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(inventory['files'])} files present; "
      f"{len(inventory['executable_sha256'])} executable hashes match.")
