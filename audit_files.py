import sys
import os
import codecs
import binascii

def audit_file(path):
    print(f"\n--- Auditing: {path} ---")
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        print(f"Raw bytes length: {len(raw)}")
        # Check for BOM
        if raw.startswith(codecs.BOM_UTF8):
            print("UTF-8 BOM detected.")
        elif raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
            print("UTF-16 BOM detected.")
        else:
            print("No BOM detected.")
        # Try decoding
        try:
            text = raw.decode('utf-8')
            print("UTF-8 decode: success")
        except Exception as e:
            print(f"UTF-8 decode: FAIL ({e})")
            text = raw.decode('utf-8', errors='replace')
        # Print invisible characters
        invis = [c for c in text if ord(c) < 32 and c not in '\n\r\t']
        if invis:
            print(f"Invisible chars found: {[binascii.hexlify(c.encode()).decode() for c in invis]}")
        else:
            print("No invisible chars found.")
        # Print line endings
        if '\r\n' in text:
            print("CRLF line endings detected.")
        elif '\r' in text:
            print("CR line endings detected.")
        elif '\n' in text:
            print("LF line endings detected.")
        else:
            print("No standard line endings detected.")
    except Exception as e:
        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    files = [
        "examples/formatting_issue.py",
        "examples/json_in_comment.py",
        "examples/markdown_heading.py",
        "examples/unused_imports.py",
        "examples/secret_key.py"
    ]
    for f in files:
        if os.path.exists(f):
            audit_file(f)
        else:
            print(f"File not found: {f}")
