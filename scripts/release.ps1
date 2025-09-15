param(
    [switch]$UploadToPyPI,
    [string]$Tag = "v0.7.2",
    [switch]$Push,
    [string]$PyPIToken
)

# Run tests
Write-Host "Running tests..."
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m pytest -q -r a
if ($LASTEXITCODE -ne 0) { throw "Tests failed; aborting release." }

# Commit changes
Write-Host "Committing changes..."
git add -A
git commit -m "chore(release): $Tag" || Write-Host "No changes to commit"

# Tag
Write-Host "Creating tag $Tag..."
git tag $Tag
if ($Push) { git push origin HEAD; git push origin $Tag }

# Build
Write-Host "Building distributions..."
.\.venv\Scripts\python.exe -m pip install --upgrade build twine
.\.venv\Scripts\python.exe -m build --sdist --wheel --outdir dist

# Optional upload
if ($UploadToPyPI) {
    # Prefer explicit parameter, fall back to environment variable PYPI_API_TOKEN
    $token = $PyPIToken
    if ([string]::IsNullOrEmpty($token)) { $token = $env:PYPI_API_TOKEN }
    if ([string]::IsNullOrEmpty($token)) {
        Write-Host "No PyPI token provided via -PyPIToken or PYPI_API_TOKEN; skipping upload." -ForegroundColor Yellow
    } else {
        Write-Host "Uploading to PyPI... (using token from environment or parameter)"
        # Use the official token username value for twine and set password from token
        $env:TWINE_USERNAME = '__token__'
        $env:TWINE_PASSWORD = $token
        .\.venv\Scripts\python.exe -m twine upload dist/*
        # Avoid leaving the token in the environment for this session
        Remove-Item Env:\TWINE_PASSWORD -ErrorAction SilentlyContinue
    }
}

Write-Host "Release script complete."
