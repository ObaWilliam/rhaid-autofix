#!/usr/bin/env bash
set -euo pipefail
cd vscode/rhaid-vscode
# Require Node and vsce
if ! command -v npx >/dev/null 2>&1; then
  echo "Please install Node.js (>=18)"
  exit 1
fi
npx --yes @vscode/vsce package
echo "VSIX created in vscode/rhaid-vscode/*.vsix"
