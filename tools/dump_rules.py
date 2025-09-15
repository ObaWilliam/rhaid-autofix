import sys, os, importlib, traceback

# Ensure local src comes first
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    rr = importlib.import_module('rhaid.register_rules')
    print('register_rules module file:', getattr(rr, '__file__', None))
    rr.register_all_rules()
    rules = importlib.import_module('rhaid.rules')
    print('rhaid.rules module file:', getattr(rules, '__file__', None))
    print('RULES:', sorted(list(rules._RULES.keys())))
    print('FIXERS:', sorted(list(rules._FIXERS.keys())))
    # Show origins for key rules
    keys = ['py:unused_import', 'py:imports_order', 'md:heading_space', 'secrets:api_key', 'json:object']
    for k in keys:
        fn = rules._RULES.get(k)
        if fn is None:
            print(k, '-> NOT REGISTERED')
        else:
            print(k, '->', getattr(fn, '__module__', None), getattr(fn, '__name__', None), 'file:', getattr(fn, '__code__', None).co_filename)
except Exception:
    traceback.print_exc()
