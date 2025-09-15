import sys


def test_dump_markdown_rules_modules():
    mods = [k for k in sys.modules if "markdown_rules" in k]
    print("Loaded modules:", mods)
