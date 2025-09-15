import sys
from pathlib import Path

# Force local src first
ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

print('sys.path[0:3]=', sys.path[:3])

try:
    import importlib
    m = importlib.import_module('rhaid')
    print('imported module file:', getattr(m, '__file__', None))
    print('rhaid.__package__:', getattr(m, '__package__', None))
    print('rhaid.__version__:', getattr(m, '__version__', 'unknown'))
except Exception as e:
    print('import error:', e)

# Run pytest programmatically on markdown tests
print('\n--- running pytest tests/test_markdown.py ---')
import pytest
exit_code = pytest.main(['tests/test_markdown.py', '-q', '-r', 'a'])
print('\npytest exit code:', exit_code)
sys.exit(exit_code)
