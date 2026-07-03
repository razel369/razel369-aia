#!/usr/bin/env python3
"""Check claude-builders-bounty + competitor activity."""
import json, urllib.request, urllib.error, re

def gh(method, path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]
    except Exception as e:
        return -1, str(e)

# 1) List claude-builders-bounty open issues
print("=" * 60)
print("claude-builders-bounty open issues")
print("=" * 60)
s, d = gh("GET", "/repos/claude-builders-bounty/claude-builders-bounty/issues?state=open&per_page=30")
if s == 200:
    for it in d:
        labels = [l.get("name") for l in it.get("labels", [])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        print(f"    comments: {it.get('comments')}, state: {it.get('state')}")

# 2) Read the high-value bounties in detail
print()
print("=" * 60)
print("Top bounties in detail")
print("=" * 60)
# 5 known bounties
for n in [1, 2, 3, 4, 5, 3128]:
    s, d = gh("GET", f"/repos/claude-builders-bounty/claude-builders-bounty/issues/{n}")
    if s == 200:
        labels = [l.get("name") for l in d.get("labels", [])]
        print(f"  #{n} [{','.join(labels)}] {d.get('title')}")
        print(f"    body: {d.get('body','')[:400]}")

# 3) Find PRs claiming each bounty
print()
print("=" * 60)
print("PRs claiming each bounty")
print("=" * 60)
s, d = gh("GET", "/search/issues?q=repo:claude-builders-bounty/claude-builders-bounty+is:pr&per_page=20")
if s == 200:
    for it in d.get("items",[]):
        # Find issue reference in body
        body = it.get("body","")
        m = re.search(r"closes\s*#(\d+)|fixes\s*#(\d+)", body, re.IGNORECASE)
        ref = m.group(1) or m.group(2) if m else "?"
        print(f"  PR #{it.get('number')} → bounty #{ref}  {it.get('state'):8}  by {it.get('user',{}).get('login'):20}  {it.get('title')[:60]}")
