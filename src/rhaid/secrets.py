import re
from .results import RuleResult

_P = {
    "secret:aws_access_key": r"AKIA[0-9A-Z]{16}",
    "secret:github_pat": r"ghp_[A-Za-z0-9]{32,}",
    "secret:private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
    "secret:stripe_api_key": r"sk_test_[A-Za-z0-9]{16,}",
}


def r_secret(path, content, ctx):
    from .rules import debug_print

    debug_print(f"[TRACE secrets:api_key] path={path}")
    out = []
    for rid, pat in _P.items():
        m = re.search(pat, content)
        debug_print(
            f"[TRACE secrets:api_key] checking {rid} with pattern {pat}: found={bool(m)}"
        )
        if m:
            out.append(
                RuleResult(
                    id="secrets:api_key",
                    message=f"Potential secret detected ({rid}).",
                    severity="error",
                    path=path,
                    line=content[: m.start()].count("\n") + 1,
                    col=1,
                )
            )
    debug_print(f"[TRACE secrets:api_key] issues={out}")
    return out
