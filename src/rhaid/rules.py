# Ensure all rules are registered at import time
## Do not call register_all_rules() at module level; registration should be triggered in CLI and test entry points only

# rules.py

from typing import Callable, List, Dict, Tuple
import re
import json
import sys
import os
import glob
import importlib.util
from rhaid.results import RuleResult, FixResult


# Registry singleton
class _Registry:
    RULES: Dict[str, Callable[[str, str, dict], List[RuleResult]]] = {}
    FIXERS: Dict[str, Callable[[str, str, List[RuleResult], dict], FixResult]] = {}


_RULES = _Registry.RULES
_FIXERS = _Registry.FIXERS


_env_val = os.environ.get("RHAID_RULE_DEBUG", "").lower()
DEBUG = _env_val in ("1", "true", "yes")
# Allow explicit suppression via env or --json, and allow forcing debug to stderr
SUPPRESS_DEBUG = False
FORCE_DEBUG_STDERR = os.environ.get("RHAID_DEBUG_STDERR", "").lower() in (
    "1",
    "true",
    "yes",
)
if hasattr(sys, "argv") and "--json" in sys.argv and not FORCE_DEBUG_STDERR:
    SUPPRESS_DEBUG = True
if os.environ.get("RHAID_SUPPRESS_DEBUG", "").lower() in ("1", "true", "yes"):
    SUPPRESS_DEBUG = True


def debug_print(*a, **kw):
    """Print debug messages to stderr when DEBUG is enabled and not suppressed.

    Usage: debug_print("msg")
    """
    if not (DEBUG and not SUPPRESS_DEBUG):
        return
    # default to stderr so JSON on stdout stays clean
    if "file" not in kw:
        kw["file"] = sys.stderr
    print(*a, **kw)


def rule(id: str):
    """Decorator to register a rule."""
    import sys

    def deco(fn):
        suppress_debug = SUPPRESS_DEBUG
        if not suppress_debug:
            print(
                f"[rhaid.rules] Registering rule: {id} from {fn.__module__}.{fn.__name__}",
                file=sys.stderr,
            )
        existing = _RULES.get(id)
        if existing and existing is not fn:
            raise RuntimeError(
                f"Duplicate rule id '{id}': "
                f"new={fn.__module__}.{fn.__name__} "
                f"already={existing.__module__}.{existing.__name__}"
            )
        _RULES[id] = fn
        return fn

    return deco


def fixer(id: str) -> Callable:
    """Decorator to register a fixer."""

    def deco(fn):
        debug_print(f"[fixers] register {id} -> {fn.__name__}")
        _FIXERS[id] = fn
        return fn

    return deco


def load_plugins(plugin_dir: str = "plugins"):
    """Dynamically load rule/fixer plugins from a directory."""
    if not os.path.isdir(plugin_dir):
        return
    for pyfile in glob.glob(os.path.join(plugin_dir, "*.py")):
        modname = f"plugin_{os.path.splitext(os.path.basename(pyfile))[0]}"
        spec = importlib.util.spec_from_file_location(modname, pyfile)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            debug_print(f"[plugins] loaded {modname} from {pyfile}")


def get_rule_priority(rule_id: str, config: dict = None) -> int:
    """Get priority for a rule from config, default 10."""
    if config and "priorities" in config:
        return config["priorities"].get(rule_id, 10)
    return 10


_SUPPRESS_RE = re.compile(r"rhaid:ignore\s+([a-z0-9:_\-]+)", re.IGNORECASE)


def filter_suppressions(content: str, issues: List[RuleResult]) -> List[RuleResult]:
    """Filter out suppressed issues from content."""
    ids = {m.group(1).lower() for m in _SUPPRESS_RE.finditer(content or "")}
    return [it for it in issues if it.id.lower() not in ids] if ids else issues


def run_rules(path: str, content: str, ctx: dict, registry=None) -> List[RuleResult]:
    """Run all registered rules on content."""
    if registry is None:
        registry = _RULES
    # If no rules are currently registered, attempt a safe, idempotent
    # registration so callers don't silently run with an empty registry.
    if not registry:
        try:
            # Defer import to avoid circular imports at module import time.
            import importlib

            rr = importlib.import_module("rhaid.register_rules")
            if hasattr(rr, "register_all_rules"):
                rr.register_all_rules()
            registry = _RULES
        except Exception:
            # If auto-registration fails, continue with whatever we have.
            pass
    res: List[RuleResult] = []
    debug_print(f"[engine] rules: {list(registry.keys())}")
    for rid, fn in registry.items():
        issues = fn(path, content, ctx)
        debug_print(f"[engine] {rid}: {len(issues)}")
        res.extend(issues)
    return res


def apply_fixers(
    path: str, content: str, issues: List[RuleResult], ctx: dict
) -> Tuple[str, List[str]]:
    """Apply relevant fixers to content."""
    updated = content
    notes: List[str] = []
    by_id: Dict[str, List[RuleResult]] = {}
    for it in issues:
        by_id.setdefault(it.id, []).append(it)
    for rid, fx in _FIXERS.items():
        rel = by_id.get(rid, [])
        if not rel:
            continue
        fr = fx(path, updated, rel, ctx)
        if fr.applied:
            updated = fr.content
            notes.extend(fr.notes)
    return updated, notes


# -------- Core rules --------


def r_trailing_newline(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect missing trailing newline at EOF."""
    if content != "" and not content.endswith("\n"):
        return [
            RuleResult(
                "format:newline",
                "No trailing newline at EOF.",
                "warning",
                path,
                line=1,
                col=1,
            )
        ]
    return []


def r_crlf(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect CRLF line endings."""
    if "\r\n" in content or ("\r" in content and "\n" not in content):
        return [
            RuleResult(
                "format:crlf", "CRLF detected; prefer LF.", "info", path, line=1, col=1
            )
        ]
    return []


def r_tabs(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect tab characters in content (cap at 10 hits)."""
    out: List[RuleResult] = []
    for i, ln in enumerate(content.splitlines(), 1):
        idx = ln.find("\t")
        if idx != -1:
            out.append(
                RuleResult(
                    "format:tabs",
                    "Tabs detected; prefer spaces.",
                    "info",
                    path,
                    line=i,
                    col=idx + 1,
                )
            )
            if len(out) >= 10:
                break
    return out


def r_spacing(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """
    Flag extra spaces around a single assignment '='.
    Avoid matching comparison/augmented operators: ==, >=, <=, !=, :=, +=, etc.
    """
    out: List[RuleResult] = []
    # Match extra spaces before or after a single '=' (not ==, etc.)
    pattern = re.compile(r"(\w+)\s+=\s{2,}\S|\S\s{2,}=\s*\S")
    for i, line in enumerate(content.splitlines(), 1):
        m = pattern.search(line)
        if m:
            col = m.start() + 1
            out.append(
                RuleResult(
                    "format:spacing",
                    "Extra spaces around assignment '='.",
                    "info",
                    path,
                    line=i,
                    col=col,
                )
            )
            debug_print(f"[format:spacing] {path}:{i}:{col} -> {line.rstrip()}")
    return out


def r_json_object(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """
    Flag JSON-like objects inside comment lines only:
      - Lines beginning (after leading whitespace) with '#' or '//'
    """
    out: List[RuleResult] = []
    for i, line in enumerate(content.splitlines(), 1):
        s = line.lstrip()
        is_comment = s.startswith("#") or s.startswith("//")
        debug_print(
            f"[json:object] checking line {i}: '{line.rstrip()}' is_comment={is_comment}"
        )
        if not is_comment:
            continue
        if "{" in s and "}" in s and ":" in s:
            col = line.find("{") + 1
            out.append(
                RuleResult(
                    "json:object",
                    "JSON-like object embedded in a comment.",
                    "info",
                    path,
                    line=i,
                    col=col,
                )
            )
            debug_print(f"[json:object] MATCH {path}:{i}:{col} -> {line.rstrip()}")
    return out


def r_json(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect invalid JSON files (only for *.json)."""
    if not path.lower().endswith(".json"):
        return []
    try:
        json.loads(content)
        return []
    except Exception as e:
        line = getattr(e, "lineno", None) or getattr(e, "pos", None)
        col = getattr(e, "colno", None) or getattr(e, "col", None)
        return [
            RuleResult(
                "json:parse", f"Invalid JSON: {e}", "error", path, line=line, col=col
            )
        ]
