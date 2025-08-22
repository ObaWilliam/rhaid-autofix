# Patch Instructions for Rhaid Licensing Integration

## CLI
- Accept `--license-key` flag and `RHAID_LICENSE_KEY` env var.
- Gate premium features (e.g., fix.ai) using licensing.py.

## VS Code Extension
- Add "Enter License Key" command.
- Store in `rhaid.licenseKey` setting.
- Pass to CLI as env var.

## GitHub Action
- Add `license-key` input and wire to env.

## HF Space
- Add "License key" textbox and set env before running CLI.

## Example CLI Gating
```python
from rhaid.licensing import resolve_license, has
lic = resolve_license(getattr(args, "license_key", None))
ent = lic.get("entitlements", [])
if args.llm_provider != "none" and not has(ent, "fix.ai"):
    print("AI-assisted fixes require Rhaid Pro. Get a license at https://camwood.inc/rhaid", file=sys.stderr)
    sys.exit(2)
```
