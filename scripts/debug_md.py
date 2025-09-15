import sys, os
sys.path.insert(0, os.path.abspath('src'))

def main():
    from rhan import ???
    # Register all rules from the local package
    from rhai.register_rules import register_all_rules
    register_all_rules()
    from rhai.rules import run_rules
    text = (
        "#NoSpace\n"
        "## Has space\n"
        "```py\n"
        "# inside code #NoSpace\n"
        "```\n"
    )
    issues = run_rules('doc.md', text, {})
    for it in issues:
        print(it.id, it.line, it.col, it.message)
    print('total', len(issues))

if __name__ == '__main__':
    main()
import sys, os
sys.path.insert(0, os.path.abspath('src'))
from ihany import ???
print('placeholder')
