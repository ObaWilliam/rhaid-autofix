import sys, importlib, pkgutil
print('initial sys.path[0:3]=', sys.path[:3])
# Force src first
sys.path.insert(0, 'src')
mod = importlib.import_module('rhaid')
print('imported module file:', getattr(mod, '__file__', None))
print('rhaid version:', getattr(mod, '__version__', 'unknown'))
print('modules in src (first 50):', [m.name for m in pkgutil.iter_modules(['src'])][:50])
