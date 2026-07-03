#!/usr/bin/env python3
"""Query owockibot API for the official bounty board + look at existing top PR to learn the pattern."""
import json, urllib.request, urllib.error, subprocess

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e: return -1, str(e)

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

# 1) owockibot API
print("=" * 60)
print("OWOCKIBOT API")
print("=" * 60)
for url in [
    "https://owockibot.xyz/api/bounty-board",
    "https://owockibot.xyz/api/bounty-board/stats",
    "https://owockibot.xyz/api/bounty/owk-001",
    "https://owockibot.xyz/api/bounty/owk-004",
    "https://owockibot.xyz/api/bounty/owk-005",
    "https://api.owockibot.xyz/api/bounty-board",
    "https://api.owockibot.xyz/bounty-board",
]:
    s, d = fetch(url)
    if s == 200:
        print(f"  {s} {url}")
        if isinstance(d, (dict, list)):
            print(f"    {json.dumps(d)[:600]}")
        else:
            print(f"    (str): {d[:300]}")
    else:
        print(f"  {s} {url}")

# 2) Look at top PRs to understand the format
print()
print("=" * 60)
print("OWK-001 top PRs")
print("=" * 60)
for num in [27, 13, 8, 26]:
    p = gh(f"repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/{num}")
    if isinstance(p, dict):
        print(f"\n  PR #{p.get('number')} by @{p.get('user',{}).get('login','?')}: {p.get('title')}")
        print(f"  state: {p.get('state')}, files: {p.get('changed_files')}, +{p.get('additions')}/-{p.get('deletions')}")
        print(f"  body[:800]: {(p.get('body') or '')[:800]}")
        # Check files
        files = gh(f"repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/{num}/files")
        if isinstance(files, list):
            print(f"  files added:")
            for f in files[:5]:
                print(f"    {f.get('status')} {f.get('filename')}")

# 3) Look at the owk-004 top PR
print()
print("=" * 60)
print("OWK-004 top PRs (best design)")
print("=" * 60)
for num in [34, 30, 23, 17, 12]:
    p = gh(f"repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/{num}")
    if isinstance(p, dict):
        print(f"\n  PR #{p.get('number')} by @{p.get('user',{}).get('login','?')}: {p.get('title')}")
        print(f"  body[:600]: {(p.get('body') or '')[:600]}")
        files = gh(f"repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/{num}/files")
        if isinstance(files, list):
            print(f"  files added:")
            for f in files[:10]:
                print(f"    {f.get('status')} {f.get('filename')}")
