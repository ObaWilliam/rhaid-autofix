import sys
import os

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# Centralized rule/fixer registration for Rhaid
# Rule modules are imported inside register_all_rules() to ensure
# they register against the freshly-imported `rhaid.rules` module.


def register_all_rules():
    src_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "src")
    )
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    # Import the existing 'rhaid.rules' module (if already imported) so that
    # functions like `fromrachd.rules import run_rules` keep referencing the
    # same module object. Do not delete `sys.modules` entries here because
    # callers may already hold references to the original module objects.
    import importlib

    if "rhaid.rules" in sys.modules:
        rules_mod = sys.modules["rhaid.rules"]
    else:
        rules_mod = importlib.import_module("rhaid.rules")
    rule = rules_mod.rule
    fixer = rules_mod.fixer
    # core rule helpers (used for formatting/json rules)
    r_trailing_newline = rules_mod.r_trailing_newline
    r_crlf = rules_mod.r_crlf
    r_tabs = rules_mod.r_tabs
    r_spacing = rules_mod.r_spacing
    r_json_object = rules_mod.r_json_object
    r_json = rules_mod.r_json
    # Clear the registry on the actual rules module
    rules_mod._RULES.clear()
    rules_mod._FIXERS.clear()
    # Import rule modules so their decorators/register calls run against rules_mod
    py_mod = importlib.import_module("rhaid.python_ast_rules")
    md_mod = importlib.import_module("rhaid.markdown_rules")
    sec_mod = importlib.import_module("rhaid.secrets")
    try:
        importlib.import_module("rhaid.js_rules")
    except Exception:
        # Optional JS/TS rule module - ignore if import fails
        pass
    # Python AST rules
    rule("py:imports_order")(py_mod.r_py_imports_order)
    fixer("py:imports_order")(py_mod.f_py_imports_order)
    rule("py:unused_import")(py_mod.r_py_unused_import)
    fixer("py:unused_import")(py_mod.f_py_unused_import)

    # Markdown rules
    rule("md:heading_space")(md_mod.r_hspace)
    fixer("md:heading_space")(md_mod.f_hspace)
    rule("md:unclosed_fence")(md_mod.r_fence)

    # Secrets rules
    rule("secrets:api_key")(sec_mod.r_secret)

    # Formatting rules
    rule("format:newline")(r_trailing_newline)
    rule("format:crlf")(r_crlf)
    rule("format:tabs")(r_tabs)
    rule("format:spacing")(r_spacing)

    # JSON rules
    rule("json:object")(r_json_object)
    rule("json:parse")(r_json)
    # Debug print statements moved to the end - use debug_print so suppression works
    from .rules import debug_print

    debug_print(
        f"[DEBUG register_all_rules] Registered rules: {list(rules_mod._RULES.keys())}"
    )
    debug_print(
        f"[DEBUG register_all_rules] Registered fixers: {list(rules_mod._FIXERS.keys())}"
    )
