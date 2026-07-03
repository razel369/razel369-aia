#!/usr/bin/env python3
"""Get all Spectral-Finance/lux bounties."""
import json, urllib.request, urllib.error

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

# 1) All open issues in Spectral-Finance/lux
print("=" * 60)
print("Spectral-Finance/lux open issues")
print("=" * 60)
s, d = gh("/repos/Spectral-Finance/lux/issues?state=open&per_page=100")
if s == 200:
    print(f"  total: {len(d)}")
    bounty_issues = []
    for it in d:
        if "pull_request" in it: continue
        title = it.get("title","")
        # Check if it's a bounty
        if "$" in title or "bounty" in title.lower() or "[Bounty" in title:
            bounty_issues.append(it)
    print(f"  bounty-related: {len(bounty_issues)}")
    for it in bounty_issues:
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {title[:80]}")
        # Check comments for USDC address
        print(f"    state: {it.get('state')}, comments: {it.get('comments')}")
    # Now fetch bodies for the bounty issues
    print()
    print("=" * 60)
    print("Bounty issue bodies + payment mechanism")
    print("=" * 60)
    for it in bounty_issues[:15]:
        s2, d2 = gh(f"/repos/Spectral-Finance/lux/issues/{it['number']}")
        if s2 == 200:
            body = d2.get("body","") or ""
            print(f"\n--- #{it['number']} {d2.get('title')} ---")
            print(body[:1500])
            # Check comments for payout info
            s3, d3 = gh(f"/repos/Spectral-Finance/lux/issues/{it['number']}/comments?per_page=10")
            if s3 == 200:
                for c in d3:
                    cb = c.get("body","")
                    if "USDC" in cb or "payout" in cb.lower() or "address" in cb.lower() or "wallet" in cb.lower() or "0x" in cb:
                        print(f"  cmt by {c.get('user',{}).get('login')}: {cb[:400]}")
                        print("  ---")

# 2) Check if Spectral-Finance has other repos
print()
print("=" * 60)
print("Spectral-Finance org repos")
print("=" * 60)
s, d = gh("/orgs/Spectral-Finance/repos?per_page=30")
if s == 200:
    for r in d:
        print(f"  {r.get('full_name')}: {r.get('description','')[:80]}  ★{r.get('stargazers_count',0)}")

# 3) Find Algora console URL
print()
print("=" * 60)
print("Algora - check the actual API")
print("=" * 60)
import urllib.request
for url in [
    "https://api.algora.io/bounties",
    "https://api.algora.io/bounties?status=open",
    "https://api.algora.io/api/v1/bounties",
    "https://console.algora.io/api/bounties",
    "https://console.algora.io/bounties",
    "https://algora.io/api/bounties",
    "https://algora.io/bounties",
]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0","Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            print(f"  {r.status} {len(body)}b  {url}")
    except urllib.error.HTTPError as e:
        print(f"  {e.code}  {url}")
    except Exception as e:
        print(f"  err  {url}")
