"""
Run the local CLI programmatically to produce JSON scan output and then run the analysis script.
Usage: python tools\run_and_analyze.py
Produces: ci_head_scan_stdout.json and analysis.json
"""
import sys
from importlib import import_module

# Ensure local src is on path
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
src_path = str(repo_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

out_json = repo_root / 'ci_head_scan_stdout.json'
err_log = repo_root / 'ci_head_scan_stderr.log'

# Call the main() function in a redirected stdout/stderr
sys.argv = ['rhaid', 'ci_head', '--mode', 'scan', '--json']
try:
    with open(out_json, 'w', encoding='utf-8') as o, open(err_log, 'w', encoding='utf-8') as e:
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = o, e
        try:
            imod = import_module('rhaid_autofix')
            if hasattr(imod, 'main'):
                try:
                    imod.main()
                except SystemExit:
                    pass
        finally:
            sys.stdout, sys.stderr = old_out, old_err
except Exception as exc:
    print('Runner error:', exc)
    raise

# Run analysis
try:
    import importlib, json
    analyze = importlib.import_module('tools.analyze_baseline')
    # call as script
    import subprocess
    subprocess.run([sys.executable, str(repo_root / 'tools' / 'analyze_baseline.py'), str(out_json), str(repo_root / 'analysis.json')], check=True)
    print('analysis.json written')
except Exception as exc:
    print('Analysis error:', exc)
    raise
