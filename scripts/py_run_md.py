import os, sys
os.environ['PYTHONPATH'] = 'src'
print('PYTHONPATH set to', os.environ['PYTHONPATH'])
# import the local package to confirm
sys.path.insert(0, 'src')
import importlib
m = importlib.import_module('rhaid')
print('imported module file:', getattr(m, '__file__', None))

import pytest
ret = pytest.main(['tests/test_markdown.py', '-q', '-r', 'a'])
print('pytest exit code', ret)
sys.exit(ret)
