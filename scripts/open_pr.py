import os
import subprocess
import datetime

branch = f"rhaid/autofix-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
subprocess.run(["git", "checkout", "-b", branch], check=True)
subprocess.run(["git", "add", "-A"], check=True)
c = subprocess.run(["git", "commit", "-m", "rhaid: automated hygiene fixes"], capture_output=True, text=True)
if c.returncode == 0:
    subprocess.run(["git", "push", "--set-upstream", "origin", branch], check=True)
    subprocess.run(["gh", "pr", "create", "--title", "Rhaid: automated hygiene fixes", "--body", "Automated hygiene pass by Rhaid."], check=True)
    subprocess.run(["gh", "pr", "edit", "--add-label", "rhaid:auto-fix"], check=False)
else:
    print("No changes to commit.")
