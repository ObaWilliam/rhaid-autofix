"""
Generate a Rhaid baseline file from analysis.json missing fingerprints.
Usage: python tools\generate_baseline_from_analysis.py analysis.json [out_baseline]

Writes a JSON baseline with fingerprints array suitable for ci_head/rhaid_baseline.json
"""
import json, sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python tools\\generate_baseline_from_analysis.py analysis.json [out_baseline]")
    sys.exit(2)

inp = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('ci_head') / 'rhaid_baseline.json'
if not inp.exists():
    print('input not found', inp)
    sys.exit(1)

data = json.load(open(inp,'r',encoding='utf-8'))
missing = data.get('missing', [])
fps = [it.get('fingerprint') for it in missing if it.get('fingerprint')]
# Remove duplicates while preserving order
seen = set(); uniq = []
for f in fps:
    if f and f not in seen:
        seen.add(f); uniq.append(f)

baseline = {'fingerprints': uniq, 'issues': []}
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(baseline, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(f'Wrote baseline with {len(uniq)} fingerprints to {out}')
