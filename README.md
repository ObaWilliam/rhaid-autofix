# Rhaid Autofix (rhaid) — v0.7.2

Rhaid Autofix by Camwood Inc. keeps repositories healthy by scanning for formatting, secrets, and policy issues, and safely applying automated fixes where available.

Highlights

- Comprehensive repo hygiene: Python, JS/TS, Markdown/MDX, JSON, YAML, TOML, Terraform, and more
- Baseline-aware: write and respect baseline files to suppress known issues
- Fast & parallel: ThreadPoolExecutor scanning, optional caching, and CI-friendly output
- Extensible: add rules and fixers with `@rule` / `@fixer`, and (future) plugin loading
- Secure: no external code transfer unless LLM features are explicitly enabled

New in v0.7.2

- `--debug-stderr` flag and `RHAID_DEBUG_STDERR` environment variable to force debug traces to stderr even when `--json` is used. This preserves a clean JSON stdout stream for automation while still allowing diagnostic traces on stderr.
- Fixes and internal improvements preparing for release v0.7.2.

Quick examples

CLI

```powershell
rhaid --path . --mode scan --json
rhaid --path src/ --mode fix --backup --rules "+format:*,+json:*" --fix-only "+format:*"
```

Force debug traces to stderr while preserving JSON on stdout:

```powershell
rhaid --path examples\secret_key.py --json --debug-stderr
```

VS Code Extension

- Use the provided extension in `vscode/rhaid-vscode` for editor diagnostics and quick fixes.

Contributing

- Add rules and fixers in `src/rhaid/` with `@rule(id)` and `@fixer(id)`.
- Run tests with `pytest`.
- See `pyproject.toml` for packaging and versioning details.

License

MIT License — (c) 2025 Camwood Inc.

Artifacts

- Built distributions are available in `dist/` after running the build step: `dist/rhaid-0.7.2-py3-none-any.whl` and `dist/rhaid-0.7.2.tar.gz`.
