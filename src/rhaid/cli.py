"""Command-line entry for simple single-file linting.

This module provides a backwards-compatible, lightweight CLI that defers to
the full `rhaid_autofix` CLI when directory scanning flags are used. Keep
top-level imports minimal and properly ordered so linters don't complain.
"""
import sys
import os
import argparse

# Default: disable rule debug traces unless explicitly enabled.
os.environ.setdefault("RHAID_RULE_DEBUG", "0")


def main():
    from rhaid.rules import (
        _RULES,
        run_rules,
        apply_fixers,
        filter_suppressions,
        load_plugins,
        debug_print,
    )
    # Import and run centralized rule registration inside main so linters
    # don't complain about module-level imports.
    try:
        import importlib

        register_mod = importlib.import_module("rhaid.register_rules")
        register_mod.register_all_rules()
    except Exception:
        # If registration fails, let run_rules proceed; tests will surface issues
        pass
    ap = argparse.ArgumentParser(description="Rhaid Lint")
    # Support both a simple single-file CLI and the richer directory-scanning CLI
    ap.add_argument("path", nargs="?", help="File to lint (positional, single file)")
    ap.add_argument(
        "--path",
        dest="path_opt",
        help="Path to file or directory to scan (alternative to positional)",
    )
    ap.add_argument(
        "--mode",
        choices=["scan", "fix"],
        default="scan",
        help="Mode: scan or fix (used with --path)",
    )
    ap.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixers where available (legacy single-file flag)",
    )
    ap.add_argument("--plugins", default="plugins", help="Plugins directory")
    ap.add_argument("--json", action="store_true", help="Output issues as JSON")
    ap.add_argument(
        "--debug-stderr",
        action="store_true",
        help="Force debug traces to stderr even when --json is used",
    )
    ap.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write baseline file for suppressing known issues",
    )
    ap.add_argument(
        "--respect-baseline",
        action="store_true",
        help="Suppress issues present in baseline file",
    )
    args = ap.parse_args()

    # If the caller used the new directory-scanning flags, delegate to the
    # repository's full CLI implementation in `rhaid_autofix.py` so behavior is
    # consistent (baselines, scanning, threading, etc.). This keeps the simple
    # single-file CLI compatible while enabling the richer interface.
    if "--path" in sys.argv or "--mode" in sys.argv or getattr(args, "path_opt", None):
        try:
            import importlib

            ra = importlib.import_module("rhaid_autofix")
            ra.main()
            return
        except Exception as e:
            # If delegation fails, fall back to single-file CLI behavior and
            # continue.
            print(f"Warning: failed to delegate to full CLI: {e}", file=sys.stderr)

    # Baseline helpers for the single-file CLI — defer to the centralized
    # baseline implementation so the single-file behavior matches the
    # repository-scanning CLI. This ensures fingerprints use the same SHA1
    # schema and baseline file layout.
    import importlib

    baseline_mod = importlib.import_module("rhaid.baseline")

    target_path = args.path or args.path_opt
    # Informational path (same naming used historically)
    baseline_path = os.path.splitext(target_path or "")[0] + ".baseline.json"

    # If user requested debug traces to stderr explicitly, set env var for rules.py
    if args.debug_stderr or os.environ.get("RHAID_DEBUG_STDERR", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        os.environ["RHAID_DEBUG_STDERR"] = "1"

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
            "col": it.col,
        }
        for it in issues
    ]
    # Write baseline if requested — reuse central write_baseline so file layout
    # and fingerprinting are identical to the scanner-mode behavior.
    if args.write_baseline:
        # baseline_mod.write_baseline expects the start path and a flat list
        outp = baseline_mod.write_baseline(target_path or path, issues_dicts)
        if args.json:
            import json

            print(json.dumps({"issues": [], "baseline": outp}))
        else:
            print(f"Baseline written to {outp}")
        return 0

    # Respect baseline if requested — filter using centralized logic
    if args.respect_baseline:
        issues_dicts = baseline_mod.filter_new_against_baseline(target_path or path, issues_dicts)

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
