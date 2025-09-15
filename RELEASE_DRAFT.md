# Release draft for v0.7.2

Checklist:

1. Ensure tests pass locally (already done):
   $env:PYTHONPATH='src'
   .\.venv\Scripts\python.exe -m pytest -q -r a

2. Bump version (if needed): `pyproject.toml` currently shows 0.7.2.

3. Commit all changes and push to main/branch:
   git add -A
   git commit -m "chore(release): v0.7.2"
   git push origin HEAD

4. Create tag and push:
   git tag v0.7.2
   git push origin v0.7.2

5. Build distributions:
   .\.venv\Scripts\python.exe -m pip install --upgrade build
   .\.venv\Scripts\python.exe -m build --sdist --wheel --outdir dist

6. Upload to PyPI:
   .\.venv\Scripts\python.exe -m pip install --upgrade twine
   .\.venv\Scripts\python.exe -m twine upload dist/*

7. Create GitHub release using tag v0.7.2, paste `RELEASE_NOTES.md`.

8. Publish VS Code extension (if desired) using `scripts/build_vsix.sh` or the VS Code Marketplace workflow.

Notes:

- If CI fails due to pytest basetemp permission issues, add `--basetemp=.pytest_tmp` to `pytest.ini` under `addopts`.
- Ensure you have credentials for PyPI and GitHub actions set up in CI.
