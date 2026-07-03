#!/usr/bin/env python3
"""Look at lux repo + HELPDESK-AI bounties."""
import json, urllib.request, urllib.error, base64, re

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

# 1) lux repo + all open issues
print("=" * 60)
print("lux repo")
print("=" * 60)
s, d = gh("/repos/lux/lux")
if s == 200:
    print(f"  full_name: {d.get('full_name')}")
    print(f"  desc: {d.get('description','')[:200]}")
    print(f"  ★ {d.get('stargazers_count')}  fork: {d.get('forks_count')}")
    print(f"  default_branch: {d.get('default_branch')}")
    print(f"  created: {d.get('created_at')}")
s, d = gh("/repos/lux/lux/issues?state=open&per_page=30")
if s == 200:
    print(f"\n  open issues: {len(d)}")
    for it in d:
        if "pull_request" in it: continue
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        body = it.get("body","") or ""
        if "USDC" in body or "payout" in body.lower() or "Address" in body or "wallet" in body.lower() or "Algora" in body or "$" in body:
            print(f"    body: {body[:600]}")
else:
    # Try other lux repos
    for name in ["lux-network","lux-ai","lux-core","lux-protocol"]:
        s2, d2 = gh(f"/repos/{name}/{name.split('-')[-1]}")
        if s2 == 200:
            print(f"  found: {name}: {d2.get('description','')[:80]}")

# 2) Find the actual lux repo by searching for the bounty issue
print()
print("=" * 60)
print("Find lux repo by issue #67")
print("=" * 60)
s, d = gh("/search/issues?q=repo:lux/*+Telegram+Analytics+is:issue&per_page=3")
if s == 200:
    for it in d.get("items",[])[:3]:
        print(f"  {it.get('repository_url')}")
        print(f"  #{it.get('number')} {it.get('title')[:80]}")

# 3) HELPDESK-AI
print()
print("=" * 60)
print("HELPDESK-AI bounties")
print("=" * 60)
for n in [3210, 3212, 3213]:
    s, d = gh(f"/repos/HELPDESK-AI/HELPDESK.AI/issues/{n}")
    if s == 200:
        print(f"  #{n} {d.get('title')}")
        print(f"    body: {d.get('body','')[:500]}")
        s2, d2 = gh(f"/repos/HELPDESK-AI/HELPDESK.AI/issues/{n}/comments?per_page=5")
        if s2 == 200:
            for c in d2:
                print(f"      cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:200]}")
                print("      ---")

# 4) Find "BountyScout" - the aggregator
print()
print("=" * 60)
print("BountyScout - bounty aggregator")
print("=" * 60)
s, d = gh("/repos/MarcusLunani/BountyScout")
if s == 200:
    print(f"  desc: {d.get('description','')[:200]}")
s, d = gh("/repos/MarcusLunani/BountyScout/contents")
if s == 200:
    for it in d[:15]:
        print(f"  {it.get('type','blob'):4} {it.get('name')}  ({it.get('size',0)} bytes)")
