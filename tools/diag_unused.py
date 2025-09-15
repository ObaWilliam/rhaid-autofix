import sys, os, importlib, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

fpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples', 'minimal_unused_import.py'))
print('Testing file:', fpath)
try:
    rr = importlib.import_module('rhaid.register_rules')
    rr.register_all_rules()
    rules = importlib.import_module('rhaid.rules')
    print('Registered:', sorted(list(rules._RULES.keys())))
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    print('Content preview:\n', content)
    fn = rules._RULES.get('py:unused_import')
    if not fn:
        print('py:unused_import not registered')
    else:
        print('Calling py:unused_import...')
        out = fn(fpath, content, {})
        print('Returned issues:', out)
        for it in out:
            print('ISSUE:', it.id, it.message, it.line, it.col)
except Exception:
    traceback.print_exc()
