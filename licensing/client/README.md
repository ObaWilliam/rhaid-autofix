# Rhaid Licensing Integration Documentation

## Overview
This document describes how to integrate license checks into Rhaid CLI, VS Code extension, GitHub Actions, and HF Spaces.

## License Server
- Issue and verify JWT licenses using FastAPI endpoints.
- Use RS256 for secure signing and offline verification.

## Client-Side Verification
- Use `licensing/client/rhaid/licensing.py` to verify tokens offline.
- Place `public.pem` in the client directory.

## Feature Gating
- Gate premium features (e.g., AI fixes) using license entitlements.
- Fallback gracefully to free features if license is missing/invalid.

## Integration Points
- CLI: `--license-key` flag, `RHAID_LICENSE_KEY` env var.
- VS Code: License key entry command, pass to CLI.
- GitHub Action: Add license-key input.
- HF Space: License textbox, pass env.

## Security Best Practices
- Rotate keys annually, keep old public keys for 60–90 days.
- Never crash on license failure; print upsell message.
- Keep core features open; only gate advanced/costly features.

## Example Usage
See `patch_instructions.md` for code snippets and integration details.
