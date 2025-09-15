# Housekeeping notes

- All tests pass locally with `PYTHONPATH=src`.
- CI workflow added: `.github/workflows/release.yml` triggers on tag pushes and uses `secrets.PYPI_API_TOKEN`.
- Use `scripts/release.ps1` to run a local release (it can push tags and upload to PyPI if provided a token).
- Remember to revoke any leaked PyPI tokens and create new, project-scoped ones.
