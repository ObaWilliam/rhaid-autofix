#!/usr/bin/env python3
import os, argparse, json, fnmatch, logging, sys
try:
    from licensing.client.rhaid.licensing import resolve_license, has
except ImportError:
    resolve_license = lambda x: {}
    has = lambda ent, feat: False
from concurrent.futures import ThreadPoolExecutor
from rhaid.config import Config, DEFAULT_INCLUDE, DEFAULT_EXCLUDE
from rhaid.scanner import list_files
import sys, os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# If user passed --debug-stderr on the command line, set the env var early so imports
# (which may import `rhaid.rules`) see the forced debug setting before module-level
# registration happens.
if '--debug-stderr' in sys.argv or os.environ.get('RHAID_DEBUG_STDERR', '').lower() in ('1','true','yes'):
    os.environ['RHAID_DEBUG_STDERR'] = '1'
# Remove any site-packages 'rhaid' from sys.modules to force local import
for mod in list(sys.modules):
    if mod.startswith('rhaid'):
        del sys.modules[mod]
import rhaid.rules  # Ensure all rules are registered from src/rhaid
from rhaid.rules import run_rules, apply_fixers, filter_suppressions
from rhaid.logging_utils import RunLogger
from rhaid.cache import load_cache, save_cache, file_hash
from rhaid.jsonpatch import json_patch
from rhaid import python_ast_rules, js_rules, mdx_rules, terraform_rules, toml_rules, markdown_rules, secrets  # register rules
from rhaid import baseline as baseline_mod

HINTS = {
  "format:newline": "--fix-only +format:*",
  "format:tabs": "--fix-only +format:*",
  "json:parse": "--fix-only json:*",
  "yaml:parse": "--fix-only yaml:*",
  "toml:eq_spacing": "--fix-only toml:eq_spacing",
  "py:imports_order": "--fix-only py:imports_order",
  "py:unused_import": "--fix-only py:unused_import",
  "js:imports_order": "--fix-only js:imports_order",
  "tf:eq_spacing": "--fix-only tf:eq_spacing"
}


def read(p: str) -> str:
    """Read file contents as UTF-8, ignoring errors."""
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def write(p: str, s: str) -> None:
    """Write string to file, creating directories as needed."""
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)

def _glob(expr: str) -> list:
    """Parse glob expression into list of patterns."""
    return [t.strip() for t in (expr or '').replace(',', ' ').split() if t.strip()]

def _allow(rule_id: str, globs: list, default: bool = True) -> bool:
    """Determine if rule_id is allowed by glob patterns."""
    if not globs:
        return default
    pos = [g[1:] for g in globs if g.startswith('+')]
    neg = [g[1:] for g in globs if g.startswith('-')]
    ok = any(fnmatch.fnmatch(rule_id, p) for p in (pos or ['*']))
    bad = any(fnmatch.fnmatch(rule_id, n) for n in neg)
    return ok and not bad


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    ap = argparse.ArgumentParser(description="Rhaid Autofix — Camwood Inc.")
    ap.add_argument('path', nargs='?', help='Path to file or directory to scan')
    ap.add_argument('--path', dest='path_opt', help='Path to file or directory to scan (alternative to positional)')
    ap.add_argument('--mode', choices=['scan', 'fix'], default='scan')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--include', default=None)
    ap.add_argument('--exclude', default=None)
    ap.add_argument('--backup', action='store_true')
    ap.add_argument('--llm-provider', choices=['none', 'openai'], default='none')
    ap.add_argument('--model', default='gpt-4o-mini')
    ap.add_argument('--max-chars', type=int, default=400_000)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--rules', default='')
    ap.add_argument('--fix-only', default='')
    ap.add_argument('--gha-annotate', action='store_true')
    ap.add_argument('--use-cache', action='store_true')
    ap.add_argument('--write-baseline', action='store_true')
    ap.add_argument('--respect-baseline', action='store_true')
    ap.add_argument('--debug-stderr', action='store_true', help='Force debug traces to stderr even when --json is used')
    return ap.parse_args()

def get_file_list(cfg: Config) -> list:
    """Get list of files to process."""
    if os.path.isfile(cfg.path):
        return [cfg.path]
    return list_files(cfg.path, cfg.include, cfg.exclude)

def scan_file(fp: str, cfg: Config, rglobs: list, cache: dict, use_cache: bool) -> tuple:
    try:
        content = read(fp)
    except Exception as e:
        return {"event": "read_error", "path": fp, "error": str(e)}, None

    if len(content) > cfg.max_chars:
        return {"event": "skipped_large", "path": fp, "size": len(content)}, None

    h = file_hash(content)
    if use_cache and cache.get(fp) == h:
        return {"event": "cache_hit", "path": fp}, (fp, content, [])

    # Load the rules module from the local package and execute rules.
    import importlib as _importlib
    _rules = _importlib.import_module('rhaid.rules')
    issues = _rules.run_rules(fp, content, ctx={})
    issues = _rules.filter_suppressions(content, issues)

    if rglobs:
        issues = [it for it in issues if _allow(it.id, rglobs, True)]

    return {"event": "scan", "path": fp, "issues": [it.__dict__ for it in issues]}, (fp, content, issues)

def flatten_issues(results: list) -> list:
    """Flatten issues from scan results."""
    all_issues = []
    for fp, content, issues in results:
        for it in issues:
            all_issues.append({'path': fp, 'id': it.id, 'message': it.message, 'severity': it.severity, 'line': it.line, 'col': it.col})
    return all_issues

def apply_fixes(results: list, cfg: Config, fglobs: list, baseline_mod, args, logger) -> int:
    """Apply fixes to files and return count of changed files."""
    changed = 0
    for fp, content, issues in results:
        per = [{'path': fp, 'id': it.id, 'message': it.message, 'severity': it.severity, 'line': it.line, 'col': it.col} for it in issues]
        if args.respect_baseline:
            filtered = baseline_mod.filter_new_against_baseline(fp, per)
            keep_ids = {(i['id'], i['line'], i['col']) for i in filtered}
            issues = [it for it in issues if (it.id, it.line, it.col) in keep_ids]
        tofix = [it for it in issues if _allow(it.id, fglobs, False)] if fglobs else issues
        if not tofix:
            continue
        # call the apply_fixers from the current rules module to avoid stale imports
        _rules = __import__('rhaid.rules', fromlist=['apply_fixers'])
        fixed, notes = _rules.apply_fixers(fp, content, tofix, ctx={})
        if fixed != content:
            if not args.dry_run:
                write(fp, fixed)
            changed += 1
            logger.log({'event': 'fix_applied', 'path': fp, 'notes': notes})
            if fp.lower().endswith(".json"):
                jp = json_patch(content, fixed)
                if jp:
                    logger.log({'event': 'json_patch', 'path': fp, 'ops': jp})
    return changed

def annotate_github(all_issues: list, HINTS: dict) -> None:
    """Print GitHub annotation lines for issues."""
    for it in all_issues:
        sev = {'error': 'error', 'warning': 'warning', 'info': 'notice'}
        fields = [f"file={it['path']}"]
        if it['line']:
            fields.append(f"line={it['line']}")
        if it['col']:
            fields.append(f"col={it['col']}")
        fields.append(f"title={it['id']}")
        hint = HINTS.get(it['id'])
        msg = it['message'] + (f" — hint: run `rhaid --mode fix {hint}`" if hint else "")
        print(f"::{sev.get(it['severity'], 'notice')} " + ",".join(fields) + f"::{msg}")

def main() -> None:
    """Main entry point for Rhaid Autofix CLI."""
    # Ensure logging uses stderr so we can keep stdout reserved for JSON output
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s', stream=sys.stderr)
    # Register all rules before scanning
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    try:
        from rhaid.register_rules import register_all_rules
        register_all_rules()
    except ImportError as e:
        print(f"Error importing/registering rules: {e}", file=sys.stderr)
        sys.exit(1)
    args = parse_args()
    # When JSON output is requested, raise the logging level to WARNING to avoid
    # interleaving informational messages on stdout. Debug/traces are handled
    # separately via debug_print and SUPPRESS_DEBUG in `rhaid.rules`.
    if getattr(args, 'json', False):
        logging.getLogger().setLevel(logging.WARNING)
    # Support both --path and positional path
    path = args.path_opt if getattr(args, 'path_opt', None) else args.path
    if not path:
        print("Error: Path to file or directory is required.", file=sys.stderr)
        sys.exit(1)
    # License key from flag or env
    license_key = getattr(args, "license_key", None) or os.environ.get("RHAID_LICENSE_KEY")
    lic = resolve_license(license_key)
    ent = lic.get("entitlements", [])
    # Gate premium features (example: AI fixes)
    if getattr(args, "llm_provider", None) not in (None, "none") and not has(ent, "fix.ai"):
        print("AI-assisted fixes require Rhaid Pro. Get a license at https://camwood.inc/rhaid", file=sys.stderr)
        sys.exit(2)
    include = [s.strip() for s in (args.include.split(',') if args.include else []) if s.strip()] or DEFAULT_INCLUDE
    exclude = [s.strip() for s in (args.exclude.split(',') if args.exclude else []) if s.strip()] or DEFAULT_EXCLUDE
    cfg = Config(path=path, mode=args.mode, dry_run=args.dry_run, include=include, exclude=exclude,
                backup=args.backup, llm_provider=args.llm_provider, model=args.model, max_chars=args.max_chars)
    files = get_file_list(cfg)
    logger = RunLogger(os.path.dirname(__file__))
    rglobs = _glob(args.rules)
    fglobs = _glob(args.fix_only)
    cache = load_cache(cfg.path) if args.use_cache else {}
    new_cache = dict(cache)
    results = []
    from multiprocessing import cpu_count
    from concurrent.futures import ThreadPoolExecutor
    logging.info(f"Scanning {len(files)} files with mode '{cfg.mode}'...")
    with ThreadPoolExecutor(max_workers=min(16, (cpu_count() or 8))) as ex:
        futures = [ex.submit(scan_file, f, cfg, rglobs, cache, args.use_cache) for f in files]
        for r in futures:
            rec, tup = r.result()
            logger.log(rec)
            if tup is not None:
                results.append(tup)
    if args.use_cache:
        save_cache(cfg.path, new_cache)
    all_issues = flatten_issues(results)
    if args.write_baseline:
        outp = baseline_mod.write_baseline(cfg.path, all_issues)
        logger.log({'event': 'baseline_written', 'path': cfg.path, 'output': outp})
        logging.info(f"Baseline written to {outp}")
    if args.respect_baseline:
        all_issues = baseline_mod.filter_new_against_baseline(cfg.path, all_issues)
    changed = 0
    if cfg.mode == 'fix':
        changed = apply_fixes(results, cfg, fglobs, baseline_mod, args, logger)
        logging.info(f"Files changed: {changed}")
    if args.gha_annotate:
        annotate_github(all_issues, HINTS)
    if args.json:
        print(json.dumps({'issues': all_issues, 'changed': changed}, ensure_ascii=False))
    if not all_issues:
        logging.info("No issues found.")
    else:
        logging.info(f"Total issues found: {len(all_issues)}")

if __name__ == '__main__':
    main()
