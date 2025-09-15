import os, importlib, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import importlib
print('importing package from', SRC)
mod = importlib.import_module('rhaid.markdown_rules')

cases = [
    ("doc.md", "#NoSpace\n## Has space\n```py\n# inside code #NoSpace\n```\n"),
    ("doc.md", "# Title\n```\ncode\n")
]
for name, text in cases:
    print('\n--- CASE ---')
    print('text:\n', text)
    a = mod.r_hspace(name, text, {})
    b = mod.r_fence(name, text, {})
    print('r_hspace ->', [ (it.id, it.line, it.col, it.message) for it in a ])
    print('r_fence  ->', [ (it.id, it.line, it.col, it.message) for it in b ])
