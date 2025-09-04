import inspect
from rhaid.rules import _RULES

def test_heading_rule_loaded_from_expected_file():
    fn = _RULES.get("md:heading_space")
    assert fn is not None, "md:heading_space not registered"
    src = inspect.getsource(fn)
    srcfile = inspect.getsourcefile(fn)
    assert "hash_count" in src or "NO_SPACE_AFTER_HASH" in src, (
        "Old implementation detected — active function source:\n" + src
    )
    assert srcfile and srcfile.endswith("markdown_rules.py"), f"Loaded from: {srcfile}"
