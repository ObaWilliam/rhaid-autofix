    # ...existing code...
import sys
from .results import RuleResult, FixResult
import re

_MD_EXTS = (".md", ".markdown", ".mdx")

def _is_md(path: str) -> bool:
    return path.lower().endswith(_MD_EXTS)


def r_hspace(path: str, content: str, ctx: dict):
    """
    Flag Markdown headings (1–6 #) where the FIRST char after the hash run
    is NOT whitespace (Unicode-aware, e.g., space, NBSP, tab, etc.).
    Ignore everything inside ``` fenced blocks.
    """
    from .rules import debug_print
    debug_print(f"[TRACE md:heading_space] path={path} is_md={_is_md(path)}")
    if not _is_md(path):
        debug_print(f"[TRACE md:heading_space] skipped: not a markdown file")
        return []
    out = []
    in_fence = False
    for i, ln in enumerate(content.splitlines(), 1):
        s = ln.lstrip()
        debug_print(f"[TRACE md:heading_space] line {i}: '{ln.rstrip()}'")
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        j = 0
        while j < len(ln) and ln[j].isspace():
            j += 1
        k = j
        while k < len(ln) and ln[k] == "#":
            k += 1
        hash_count = k - j
        if 1 <= hash_count <= 6:
            next_char = ln[k:k+1]
            # Fix: allow headings with no space after #
            if next_char and (not next_char.isspace() or next_char != ''):
                out.append(RuleResult(
                    "md:heading_space",
                    "Missing space after '#' in heading.",
                    "info",
                    path,
                    line=i,
                    col=j+1
                ))
    debug_print(f"[TRACE md:heading_space] issues={out}")
    return out

def f_hspace(path: str, content: str, issues, ctx):
    if not issues:
        return FixResult(False, [], content)
    def _fix_line(line: str) -> str:
        j = 0
        while j < len(line) and line[j].isspace():
            j += 1
        k = j
        while k < len(line) and line[k] == "#":
            k += 1
        hash_count = k - j
        if 1 <= hash_count <= 6:
            next_char = line[k:k+1]
            if next_char and not next_char.isspace():
                return line[:k] + " " + line[k:]
        return line
    lines = content.splitlines(keepends=True)
    fixed = "".join(_fix_line(ln) for ln in lines)
    return FixResult(fixed != content, ["Inserted space after '#' in headings."], fixed)

def r_fence(path: str, content: str, ctx: dict):
    if not _is_md(path):
        return []
    # Odd number of code fences means unclosed
    if content.count("```") % 2 != 0:
        return [RuleResult("md:unclosed_fence", "Unbalanced ``` code fences.", "warning", path, line=1, col=1)]
    return []
