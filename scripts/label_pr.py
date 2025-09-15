import json
import os
import subprocess

report = json.loads(os.popen('rhaid --path . --mode scan --json --respect-baseline').read() or '{"issues":[]}')
pr_number = os.environ.get('PR_NUMBER', os.environ.get('GITHUB_PR_NUMBER', os.environ.get('GITHUB_REF', '')))
if report.get('issues'):
    subprocess.run([
        'gh', 'pr', 'edit',
        pr_number if pr_number else '${{ github.event.number }}',
        '--add-label', 'rhaid:needs-fix'
    ], check=False)
