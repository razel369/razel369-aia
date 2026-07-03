#!/usr/bin/env python3
"""Check easy bounties + look at intuition-box + look at ClankerNation + check claimed bounties aging."""
import json, subprocess, urllib.request, urllib.error, time

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e: return -1, str(e)

# 1) Check tuangel1346/bounty-sentry#1 (the $5 USDC easy one)
print("=" * 60)
print("tuangel1346/bounty-sentry#1 ($5 USDC, 12h)")
print("=" * 60)
issue = gh("repos/tuangel1346/bounty-sentry/issues/1")
if isinstance(issue, dict):
    print(f"  title: {issue.get('title')}")
    print(f"  state: {issue.get('state')}")
    print(f"  body: {issue.get('body','')[:1500]}")
    print()
    print("  Comments:")
    comments = gh("repos/tuangel1346/bounty-sentry/issues/1/comments")
    if isinstance(comments, list):
        for c in comments[:5]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:300]}")

# 2) Check ClankerNation/OpenAgents $4k bounties
print()
print("=" * 60)
print("ClankerNation/OpenAgents ($4k bounties)")
print("=" * 60)
for n in [27, 50, 28, 51, 52]:
    issue = gh(f"repos/ClankerNation/OpenAgents/issues/{n}")
    if isinstance(issue, dict):
        title = issue.get("title","")
        if "$" in title or "Bounty" in title or "bounty" in title.lower():
            print(f"  #{n}: {title}")
            print(f"    state: {issue.get('state')}")
            body = issue.get("body","")[:500]
            print(f"    body: {body}")

# 3) Check intuition-box/Fee-Proxy-Template#2 ($1,100)
print()
print("=" * 60)
print("intuition-box/Fee-Proxy-Template#2 ($1,100 USDC)")
print("=" * 60)
issue = gh("repos/intuition-box/Fee-Proxy-Template/issues/2")
if isinstance(issue, dict):
    print(f"  title: {issue.get('title')}")
    print(f"  state: {issue.get('state')}")
    print(f"  body: {issue.get('body','')[:3000]}")
    print()
    print("  Comments:")
    comments = gh("repos/intuition-box/Fee-Proxy-Template/issues/2/comments")
    if isinstance(comments, list):
        for c in comments[:5]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:400]}")

# 4) Check owockibot for any new open bounties in the LAST 1 hour
print()
print("=" * 60)
print("OWOCKIBOT: latest bounties (looking for new open)")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/bounty-board")
if isinstance(d, list):
    # Sort by id desc
    new_b = sorted(d, key=lambda x: -(x.get("id") or 0))[:30]
    for b in new_b:
        rid = b.get("id")
        title = b.get("title","")[:50]
        reward = b.get("reward_usdc")
        status = b.get("status")
        if status == "open" or status == "claimed" or status == "submitted":
            claimer = (b.get("claimer_address") or "")[:14]
            print(f"  #{rid} ${reward} [{status}] {claimer}  {title}")

# 5) Check the GitHub trending for AI agent bounty programs
print()
print("=" * 60)
print("GITHUB: search for new bounty programs")
print("=" * 60)
queries = [
    "/claim USDC bounty",
    "bounty USDC first PR",
    "AI agent bounty paid",
    "BountyEscrow.sol",
]
for q in queries:
    r = subprocess.run(["gh","search","issues",q,"--state","open","--limit","3",
                        "--json","number,title,url,repository,body,commentsCount,labels"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try:
            results = json.loads(r.stdout)
            for it in results:
                if any(kw in (it.get("title","")+it.get("body","")).lower() for kw in ["usdc","bounty","escrow","paid"]):
                    print(f"  {it.get('repository',{}).get('nameWithOwner','')}#{it.get('number')}: {it.get('title','')[:70]}")
        except: pass
