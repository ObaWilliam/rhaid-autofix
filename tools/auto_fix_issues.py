"""
Auto-fix top-severity issues from an analysis.json file.
Usage: python tools\auto_fix_issues.py analysis.json

This script will:
- import the project's rule registry and register rules/fixers
- load analysis.json and iterate missing issues
- for each file, run the engine to get current issues
- apply available fixers (py:unused_import, py:imports_order)
- apply safe formatting fixes: replace tabs with 4 spaces, ensure trailing newline
- write updated files in-place and print a short summary
"""
import json
import os
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python tools\\auto_fix_issues.py <analysis.json>")
    sys.exit(2)

analysis_path = Path(sys.argv[1])
if not analysis_path.exists():
    print(f"analysis file not found: {analysis_path}")
    sys.exit(1)

repo_root = Path(__file__).resolve().parents[1]
# Ensure src is on sys.path
src_path = str(repo_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the rules engine from the local src package
import importlib

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    rules = importlib.import_module("rhaid.rules")
except Exception as e:
    print(f"Error importing rhaid.rules: {e}")
    raise

try:
    register_rules = importlib.import_module("rhaid.register_rules")
except Exception:
    register_rules = None

# Attempt to register rules/fixers
if register_rules and hasattr(register_rules, "register_all_rules"):
    try:
        register_rules.register_all_rules()
    except Exception as e:
        print(f"Warning: register_all_rules() raised: {e}")

with open(analysis_path, "r", encoding="utf-8") as fh:
    analysis = json.load(fh)

missing = analysis.get("missing", [])
# Group by path
by_path = {}
for it in missing:
    p = it.get("issue", {}).get("path")
    if not p:
        continue
    by_path.setdefault(p, []).append(it)

modified = []
for p, issues in by_path.items():
    fp = Path(p)
    if not fp.exists():
        print(f"skipping (not found): {p}")
        continue
    content = fp.read_text(encoding="utf-8")
    ctx = {}
    # Run engine to get live issues
    current = rules.run_rules(str(fp), content, ctx)
    # Apply available fixers
    new_content, notes = rules.apply_fixers(str(fp), content, current, ctx)
    # If format:tabs or format:newline present in current, apply simple fixes
    ids = {c.id for c in current}
    if "format:tabs" in ids:
        # Replace tabs with 4 spaces
        new_content = new_content.replace("\t", "    ")
        notes.append("Replaced tabs with 4 spaces.")
    if "format:newline" in ids:
        if not new_content.endswith("\n"):
            new_content = new_content + "\n"
            notes.append("Appended trailing newline.")
    if new_content != content:
        fp.write_text(new_content, encoding="utf-8")
        modified.append({"path": str(fp), "notes": notes})
        print(f"modified: {fp} -> {notes}")

print(f"Done. Files modified: {len(modified)}")
if modified:
    for m in modified:
        print(m["path"])
