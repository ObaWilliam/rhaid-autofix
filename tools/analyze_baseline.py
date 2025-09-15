"""Analyze scan JSON against existing baseline and produce prioritized report.

Usage:
  python tools\analyze_baseline.py scan_all.json analysis.json

Outputs JSON with:
 - total_issues
 - baseline_count
 - missing_count
 - missing (list of {fingerprint, issue})
 - top_rules (by severity-weighted count)
"""
import sys
import json
import hashlib
from collections import Counter, defaultdict

INPUT = sys.argv[1] if len(sys.argv) > 1 else 'scan_all.json'
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else 'analysis.json'
BASELINE_FILE = 'rhaid_baseline.json'

def fingerprint(path, rid, msg):
    h = hashlib.sha1()
    # match existing baseline implementation: path + "\n" + id + "\n" + message.strip()
    s = path + "\n" + rid + "\n" + (msg or '').strip()
    # use same encode form (encoding, errors)
    h.update(s.encode('utf-8', 'ignore'))
    return h.hexdigest()

scan = json.load(open(INPUT, 'r', encoding='utf-8'))
issues = scan.get('issues', [])

baseline_fps = set()
try:
    baseline = json.load(open(BASELINE_FILE, 'r', encoding='utf-8'))
    baseline_fps = set(baseline.get('fingerprints', []))
except Exception:
    baseline_fps = set()

missing = []
for it in issues:
    fp = fingerprint(it['path'], it['id'], it.get('message',''))
    if fp not in baseline_fps:
        missing.append({'fingerprint': fp, 'issue': it})

# severity weighting: error=3, warning=2, info=1
weight = {'error':3, 'warning':2, 'info':1}
rule_counter = Counter()
sev_counter = defaultdict(int)
for m in missing:
    it = m['issue']
    rule_counter[it['id']] += 1
    sev_counter[it['id']] += weight.get(it.get('severity','info'), 1)

# prioritize by severity-weighted count then raw count
prioritized = sorted(rule_counter.items(), key=lambda kv: (-sev_counter[kv[0]], -kv[1], kv[0]))

out = {
    'total_issues': len(issues),
    'baseline_fingerprints_count': len(baseline_fps),
    'missing_count': len(missing),
    'missing': missing,
    'top_rules': [{'id': rid, 'count': cnt, 'severity_weight': sev_counter[rid]} for rid,cnt in prioritized],
}
json.dump(out, open(OUTPUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"Wrote {OUTPUT}: total_issues={len(issues)} missing={len(missing)}")
