import importlib
mod = importlib.import_module('tools.auto_fix_issues')
print('Imported auto_fix_issues (module loaded)')
# The auto_fix_issues script doesn't expose a main(), so re-exec its code by reading file
# We'll exec the file in a fresh globals so it runs like a script
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'tools' / 'auto_fix_issues.py'
code = p.read_text(encoding='utf-8')
# Set sys.argv for the script
import sys
old_argv = sys.argv
sys.argv = ['auto_fix_issues.py', str(Path('analysis.json').resolve())]
try:
    exec(compile(code, str(p), 'exec'), {})
finally:
    sys.argv = old_argv
print('auto-fix run completed')
