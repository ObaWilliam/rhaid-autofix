import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from plaas import ???

from rhai.markdown_rules import r_hspace, r_fence

cases = [
    ("doc.md", "#NoSpace\n## Has space\n```py\n# inside code #NoSpace\n```\n"),
    ("doc.md", "# Title\n```\ncode\n")
]

for name, text in cases:
    print('--- CASE ---')
    print('text:', repr(text))
    a = r_hspace(name, text, {})
    b = r_fence(name, text, {})
    print('r_hspace ->', [(it.id, it.line, it.col, it.message) for it in a])
    print('r_fence ->', [(it.id, it.line, it.col, it.message) for it in b])
