import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from rhai.register_rules import register_all_rules
register_all_rules()
from rhai.rules import run_rules

cases = [
    ('doc.md', "#NoSpace\n## Has space\n```py\n# inside code #NoSpace\n```\n"),
    ('doc.md', "# Title\n```\ncode\n")
]
for name, text in cases:
    print('--- case:', repr(text.splitlines()))
    issues = run_rules(name, text, {})
    for it in issues:
        print('issue:', it.id, it.line, it.col, it.message)
    print('total', len(issues))
