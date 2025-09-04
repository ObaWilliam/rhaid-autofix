



# Suppress debug output if --json is present in sys.argv
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if '--json' in sys.argv:
    os.environ['RHAID_RULE_DEBUG'] = '0'

import argparse
import os
import rhaid.register_rules  # Centralized rule registration

def main():
    from rhaid.rules import _RULES, run_rules, apply_fixers, filter_suppressions, load_plugins, debug_print
    rhaid.register_rules.register_all_rules()
    ap = argparse.ArgumentParser(description="Rhaid Lint")
    ap.add_argument("path", help="File to lint")
    ap.add_argument("--fix", action="store_true", help="Apply fixers where available")
    ap.add_argument("--plugins", default="plugins", help="Plugins directory")
    ap.add_argument("--json", action="store_true", help="Output issues as JSON")
    ap.add_argument("--debug-stderr", action="store_true", help="Force debug traces to stderr even when --json is used")
    ap.add_argument("--write-baseline", action="store_true", help="Write baseline file for suppressing known issues")
    ap.add_argument("--respect-baseline", action="store_true", help="Suppress issues present in baseline file")
    args = ap.parse_args()

    # Baseline logic (must be after args is defined)
    baseline_path = os.path.splitext(args.path)[0] + ".baseline.json"
    def load_baseline():
        if os.path.isfile(baseline_path):
            import json
            with open(baseline_path, "r", encoding="utf-8") as f:
                return set(json.load(f).get("fingerprints", []))
        return set()
    def issue_fingerprint(it):
        return f"{it['path']}:{it['id']}:{it['message']}"
    baseline_path = os.path.splitext(args.path)[0] + ".baseline.json"

    args = ap.parse_args()

    # Baseline logic
    baseline_path = os.path.splitext(args.path)[0] + ".baseline.json"
    def load_baseline():
        if os.path.isfile(baseline_path):
            import json
            with open(baseline_path, "r", encoding="utf-8") as f:
                return set(json.load(f).get("fingerprints", []))
        return set()
    def issue_fingerprint(it):
        return f"{it['path']}:{it['id']}:{it['message']}"

    # If user requested debug traces to stderr explicitly, set env var for rules.py
    if args.debug_stderr or os.environ.get('RHAID_DEBUG_STDERR', '').lower() in ('1','true','yes'):
        os.environ['RHAID_DEBUG_STDERR'] = '1'

    # Suppress debug output is handled via environment variable and rules.py

    load_plugins(args.plugins)

    path = args.path
    debug_print(f"[DEBUG] Registered rules: {list(_RULES.keys())}")
    if not os.path.isfile(path):
        if args.json:
            import json
            print(json.dumps({"issues": [], "error": f"not a file: {path}"}))
            return 2
        else:
            debug_print(f"error: not a file: {path}")
            return 2

    with open(path, "r", encoding="utf-8", newline="") as f:
        content = f.read()
    debug_print(f"[TRACE CLI] Scanning file: {path}")
    debug_print(f"[TRACE CLI] File extension: {os.path.splitext(path)[1]}")
    debug_print(f"[TRACE CLI] File content:\n{content}")

    ctx = {}
    issues = run_rules(path, content, ctx, _RULES)
    debug_print(f"[DEBUG] Issues found: {issues}")
    issues = filter_suppressions(content, issues)
    issues_dicts = [
        {
            "id": it.id,
            "message": it.message,
            "severity": it.severity,
            "path": it.path,
            "line": it.line,
            "col": it.col
        } for it in issues
    ]
    # Write baseline if requested
    if args.write_baseline:
        import json
        fingerprints = sorted({issue_fingerprint(it) for it in issues_dicts})
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump({"fingerprints": fingerprints}, f, ensure_ascii=False, indent=2)
        if args.json:
            print(json.dumps({"issues": [], "baseline": baseline_path}))
        else:
            print(f"Baseline written to {baseline_path}")
        return 0
    # Respect baseline if requested
    if args.respect_baseline:
        baseline = load_baseline()
        issues_dicts = [it for it in issues_dicts if issue_fingerprint(it) not in baseline]

    if args.json:
        import json
        print(json.dumps({"issues": issues_dicts}))
        return 0

    if not issues:
        print("No issues.")
        return 0

    for it in issues:
        print(f"{it.path}:{it.line}:{it.col}: {it.severity} {it.id}: {it.message}")

    if args.fix:
        updated, notes = apply_fixers(path, content, issues, ctx)
        if updated != content:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(updated)
            for n in notes:
                print(f"fix: {n}")
    return 0

def entry():
    raise SystemExit(main())

if __name__ == "__main__":
    entry()
