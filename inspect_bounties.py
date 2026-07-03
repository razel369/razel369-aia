#!/usr/bin/env python3
"""Inspect best USDC bounties + look at owockibot."""
import json, subprocess

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

bounties = [
    ("tuangel1346/bounty-sentry", 1),
    ("cyrilawoyemi99-max/owockibot-bounty-sync-", 1),
    ("cyrilawoyemi99-max/owockibot-bounty-sync-", 4),
    ("cyrilawoyemi99-max/owockibot-bounty-sync-", 5),
    ("intuition-box/Fee-Proxy-Template", 2),
    ("runxhq/runx", 77),
    ("HavenOnStellar/Haven_Docs", 3),
]

for repo, num in bounties:
    print(f"\n==== {repo} #{num} ====")
    issue = gh(f"repos/{repo}/issues/{num}")
    if isinstance(issue, dict):
        print(f"  title: {issue.get('title')}")
        print(f"  state: {issue.get('state')}")
        print(f"  labels: {[l.get('name','') for l in issue.get('labels',[])]}")
        print(f"  body: {issue.get('body','')[:2000]}")
        print()
        print("  Comments:")
        comments = gh(f"repos/{repo}/issues/{num}/comments")
        if isinstance(comments, list):
            for c in comments[:5]:
                print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:300]}")

# Look at owockibot info
print("\n==== OWOCKIBOT info ====")
owocki = gh("users/cyrilawoyemi99-max")
if isinstance(owocki, dict):
    print(f"  user: {owocki.get('login')}, bio: {owocki.get('bio','')[:200]}")

# Check what owockibot-bounty-sync- repo is
print()
repo_info = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-")
if isinstance(repo_info, dict):
    print(f"  desc: {repo_info.get('description','')}")
    print(f"  stars: {repo_info.get('stargazers_count')}")
    print(f"  html: {repo_info.get('html_url')}")

# Check intuition-box org
print()
for r in (gh("orgs/intuition-box/repos?per_page=10") or []):
    print(f"  {r.get('name')}: {r.get('description','')[:80]}")
