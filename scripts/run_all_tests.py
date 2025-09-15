import os, sys, importlib
# Ensure local src first
sys.path.insert(0, 'src')
os.environ['PYTHONPATH'] = 'src'
print('sys.path[0:3]=', sys.path[:3])
import pytest
ret = pytest.main(['-q', '-r', 'a'])
print('pytest exit code', ret)
sys.exit(ret)
