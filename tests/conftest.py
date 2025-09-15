import sys
from pathlib import Path

# Ensure the repository's `src` directory is first on sys.path so tests
# import the local source rather than any installed or build artifacts.
ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def pytest_configure(config):
    # Make the insertion visible when running tests with verbose import tracing
    config._rhaid_src_forced = SRC
    # Keep tests importing from local `src` by ensuring it's first on sys.path.
    # (Transient diagnostic prints were removed.)
    # Ensure Markdown rules are imported and registered for all tests
    import rhaid.markdown_rules  # noqa: F401
