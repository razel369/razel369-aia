#!/usr/bin/env python3
"""Check cocohub-mobileapp bounties + look for TariProject 2308."""
import json, urllib.request, urllib.error

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

# 1) cocohub-mobileapp bounties
print("=" * 60)
print("cocohub-mobileapp bounties")
print("=" * 60)
for issue in [50, 51, 52, 47, 48, 49]:
    s, d = gh("GET", f"/repos/cocohub-mobileapp/cocohub-main/issues/{issue}")
    if s == 200:
        labels = [l.get("name") for l in d.get("labels", [])]
        print(f"  #{issue} [{','.join(labels)}] {d.get('title')}")
        print(f"    body: {d.get('body','')[:200]}")
        s2, d2 = gh("GET", f"/repos/cocohub-mobileapp/cocohub-main/issues/{issue}/comments?per_page=20")
        if s2 == 200 and d2:
            print(f"    comments: {len(d2)}")
            for c in d2[:3]:
                print(f"      by {c.get('user',{}).get('login')}: {c.get('body','')[:200]}")
    else:
        print(f"  #{issue} {s}")

# 2) TariProject 2308
print()
print("=" * 60)
print("TariProject 2308 status")
print("=" * 60)
s, d = gh("GET", "/repos/tari-project/tari-ootle/issues/2308")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"body: {d.get('body','')[:500]}")
    s2, d2 = gh("GET", "/repos/tari-project/tari-ootle/issues/2308/comments?per_page=20")
    if s2 == 200:
        for c in d2:
            print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
            print("  ---")
# PRs linked
s, d = gh("GET", "/search/issues?q=repo:tari-project/tari-ootle+2308+is:pr")
if s == 200:
    for it in d.get("items",[]):
        print(f"  PR #{it.get('number')} {it.get('state')}: {it.get('title')[:80]}")

# 3) claude-builders-bounty 3128 (the new "PAYMENT: USDC on Base" issue)
print()
print("=" * 60)
print("claude-builders-bounty #3128 - PAYMENT: USDC on Base wallet")
print("=" * 60)
s, d = gh("GET", "/repos/dsp-dr/guillotine/issues/3128") if False else gh("GET", "/search/issues?q=3128+repo:dsp-dr/guillotine")
# Actually let me just find what repo claude-builders-bounty is in
s, d = gh("GET", "/search/repositories?q=claude-builders-bounty&per_page=3")
if s == 200:
    for it in d.get("items",[]):
        print(f"  ★{it.get('stargazers_count',0):>4}  {it.get('full_name')}: {it.get('description','')[:80]}")
