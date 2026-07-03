#!/usr/bin/env python3
"""Get owk-001 + owk-004 exact requirements + look at top PR files to understand the pattern."""
import json, subprocess, urllib.request, urllib.error, base64

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

def gh_raw(path):
    """Get raw file content."""
    r = subprocess.run(["gh","api",path,"--jq",".content"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout:
        try:
            return base64.b64decode(r.stdout).decode("utf-8", errors="replace")
        except: return r.stdout
    return None

# 1) owk-001 issue (full)
print("=" * 60)
print("OWK-001 full issue")
print("=" * 60)
issue = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/1")
if isinstance(issue, dict):
    print(f"  body FULL:\n{issue.get('body','')}")
    print()
    print("  Comments:")
    comments = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/1/comments")
    if isinstance(comments, list):
        for c in comments[:10]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:500]}")

# 2) owk-004 issue
print()
print("=" * 60)
print("OWK-004 full issue")
print("=" * 60)
issue = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/4")
if isinstance(issue, dict):
    print(f"  body FULL:\n{issue.get('body','')}")
    print()
    print("  Comments:")
    comments = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/4/comments")
    if isinstance(comments, list):
        for c in comments[:10]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:500]}")

# 3) Look at top submission file content
print()
print("=" * 60)
print("OWK-004 top PR (PR #34 by Godel-Smith) — sample SVG")
print("=" * 60)
# Get the first SVG file
files = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/34/files")
if isinstance(files, list):
    for f in files[:3]:
        fname = f.get("filename","")
        print(f"\n  --- {fname} ---")
        content = gh_raw(f"repos/cyrilawoyemi99-max/owockibot-bounty-sync-/contents/{fname}?ref=refs/pull/34/head")
        if content:
            print(content[:1500])

# 4) Check owk-005 for security audit details
print()
print("=" * 60)
print("OWK-005 details")
print("=" * 60)
issue = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/5")
if isinstance(issue, dict):
    print(f"  body: {issue.get('body','')[:3000]}")
    print()
    print("  Comments:")
    comments = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/5/comments")
    if isinstance(comments, list):
        for c in comments[:10]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:500]}")
