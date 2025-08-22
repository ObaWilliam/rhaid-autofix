# Rhaid Licensing Onboarding Guide

Welcome to Rhaid Pro! This guide will help you set up licensing for premium features in CLI, VS Code, CI, and web apps.

## 1. Get Your License Key
- Purchase a Pro/Team/Enterprise plan at https://camwood.inc/rhaid
- Receive your JWT license key via email or dashboard

## 2. CLI Setup
- Run Rhaid CLI with your license key:
  ```sh
  rhaid --license-key <YOUR_LICENSE_KEY> --path . --mode fix --llm-provider openai
  ```
- Or set the environment variable:
  ```sh
  export RHAID_LICENSE_KEY=<YOUR_LICENSE_KEY>
  rhaid --path . --mode fix --llm-provider openai
  ```
- Premium features (e.g., AI fixes) require a valid license.

## 3. VS Code Extension
- Open Command Palette: "Rhaid: Enter License Key"
- Paste your license key; it will be stored in `rhaid.licenseKey` setting
- Premium features will be enabled if the license is valid

## 4. GitHub Actions
- Add `license-key` input to your workflow:
  ```yaml
  - name: Run Rhaid
    run: |
      export RHAID_LICENSE_KEY=${{ secrets.RHAID_LICENSE_KEY }}
      rhaid --path . --mode fix --llm-provider openai
  ```

## 5. HF Space / Web App
- Enter your license key in the "License Key" textbox
- Premium features will be enabled for your session

## 6. Troubleshooting
- If your license is invalid or expired, premium features will be disabled and you’ll see an upsell message
- For help, contact support@camwood.inc

## 7. Security
- Your license key is a JWT signed with RS256; never share your private key
- Keys are rotated annually for security

---
Thank you for choosing Rhaid Pro!
