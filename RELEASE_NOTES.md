v0.7.2
-------

- Added `--debug-stderr` CLI flag and `RHAID_DEBUG_STDERR` environment variable to force debug traces to stderr even when `--json` output is requested.
- Ensured debug traces are suppressed from stdout by default when `--json` is present.
- Bumped package version to 0.7.2.

Notes
- Artifacts (sdist/wheel) can be produced with `python -m build` in an environment with `build` installed.

Highlights

- Add `--debug-stderr` flag and `RHAID_DEBUG_STDERR` env var to force debug traces to stderr when `--json` is used. This keeps stdout JSON clean.
- Bugfix: ensure debug traces are suppressed from stdout when `--json` is present by default.
- Internal: Harden rule registration to avoid import-shadowing and provide a safe auto-registration fallback when `run_rules()` is invoked before explicit registration.
- Tests: Fixed markdown rule handling and deterministic test execution order; added `tests/conftest.py` to ensure tests import from `src`.

Packaging

- Build artifacts in `dist/`:

```text
dist/rhaid-0.7.2-py3-none-any.whl
dist/rhaid-0.7.2.tar.gz
```

- To build locally (from repository root):

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m pip install --upgrade build
.\.venv\Scripts\python.exe -m build --sdist --wheel --outdir dist
```

Publishing

- Tag and push: `git tag v0.7.2 && git push --tags`
- Upload to PyPI: `twine upload dist/*`

Notes

- One integration test requires a running Stripe webhook server (skipped in CI by default).
- If pytest fails to clean up OS temp directories on Windows, use `--basetemp=.pytest_tmp` or fix permissions on the temp folder.
