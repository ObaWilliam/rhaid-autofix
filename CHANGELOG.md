# Changelog

## 0.7.2 - 2025-09-04

- Add `--debug-stderr` flag and `RHAID_DEBUG_STDERR` env var to force debug traces to stderr when `--json` is used.
- Fix: Ensure debug traces are suppressed from stdout when `--json` is present.
- Fix: Harden rule registration and add defensive auto-registration to `run_rules()`.
- Tests: Improve deterministic behavior and ensure tests import from local `src`.
