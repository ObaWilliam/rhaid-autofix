# Rhaid VS Code Extension — v0.4.0

![Rhaid Logo](../../asset/Rhaid_Autofix_Logo_128x128.png)

![Rhaid Extension Banner](https://raw.githubusercontent.com/camwood/rhaid-autofix/main/assets/vscode-banner.png)

## Overview
Rhaid brings automated repo hygiene and AI guardrails to your VS Code workflow. Instantly scan, fix, and maintain code quality with diagnostics, quick fixes, and fix-on-save.

---

## Features
- **Scan Workspace:** Detect issues across your project with one command.
- **Quick Fixes:** Instantly fix issues in the current file.
- **Fix on Save:** Optionally auto-fix files every time you save.
- **Diagnostics:** Inline error/warning/info annotations powered by Rhaid CLI.
- **Pro License Support:** Enter your license key for advanced features.

---

## Screenshots

![Scan Workspace](https://raw.githubusercontent.com/ObaWilliam/rhaid-autofix/main/assets/vscode-scan.png)
*Scan your entire workspace for issues.*

![Quick Fix](https://raw.githubusercontent.com/ObaWilliam/rhaid-autofix/main/assets/vscode-quickfix.png)
*Apply quick fixes to files with a single click.*

---

## Installation
**Recommended for most users:**

1. Install Rhaid CLI globally:
   ```sh
   pip install --upgrade rhaid-autofix
   ```
2. Install this extension from the VS Code Marketplace or via `.vsix` file.
3. If `rhaid` is not found, set the path to the Rhaid binary in VS Code settings (`rhaid.pathToBinary`).

**Advanced/Isolated install (optional):**
- Use [pipx](https://pipxproject.github.io/pipx/) for isolated CLI installs:
  ```sh
  pipx install rhaid-autofix
  ```

---

## Usage
- **Scan Workspace:**
  ```sh
  rhaid --path . --mode scan --json
  ```
- **Fix Current File:**
  ```sh
  rhaid --path path/to/file.py --mode fix --json
  ```
- **Show Help:**
  ```sh
  rhaid --help
  ```

---

## Configuration
Go to VS Code settings and search for `Rhaid`:
- `rhaid.pathToBinary`: Path to the Rhaid CLI binary (if not in PATH).
- `rhaid.fixOnSave`: Enable/disable fix on save.
- `rhaid.scanArgs`: Custom scan arguments.
- `rhaid.fixArgs`: Custom fix arguments.

---

## Troubleshooting
- If you see 'Rhaid binary not found', install the CLI and set the correct path in settings.
- If you get 'unrecognized arguments', check the CLI help for supported options.
- For advanced usage, see [Rhaid CLI documentation](https://github.com/camwood/rhaid-autofix).

---

## Accessibility & Support
- Keyboard accessible commands and actions.
- Works with all major VS Code themes.
- For help, open an issue on [GitHub](https://github.com/ObaWilliam/rhaid-autofix/issues).

---

## Video Demo
[![Watch the demo](https://img.youtube.com/vi/DEMO_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=DEMO_VIDEO_ID)

---

## Marketplace Keywords
`repo hygiene`, `ai guardrails`, `autofix`, `linter`, `code quality`, `security`, `automation`, `quick fix`, `diagnostics`, `devops`, `compliance`, `python`, `markdown`, `json`, `yaml`, `terraform`, `mdx`, `toml`

---

## License
MIT

---

*Rhaid: Automated hygiene for modern codebases. Fast. Reliable. AI-powered.*
