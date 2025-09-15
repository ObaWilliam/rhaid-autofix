"""
Normalize scan JSON file encoding to UTF-8 and write out a clean JSON file.
Usage: python tools\normalize_scan.py input.json output.json
"""
import sys
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: python tools\\normalize_scan.py input.json output.json")
    sys.exit(2)

inp = Path(sys.argv[1])
out = Path(sys.argv[2])
if not inp.exists():
    print('input not found', inp)
    sys.exit(1)

b = inp.read_bytes()
# Try UTF-8, then UTF-16 LE/BE, then latin1
for enc in ('utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1'):
    try:
        s = b.decode(enc)
        # quick sanity check: must start with '{' or '['
        ss = s.lstrip()
        if ss.startswith('{') or ss.startswith('['):
            out.write_text(s, encoding='utf-8')
            print(f'Wrote {out} (decoded with {enc})')
            sys.exit(0)
    except Exception:
        continue
print('Failed to decode file with known encodings')
sys.exit(1)
