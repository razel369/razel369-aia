#!/usr/bin/env python3
"""Find correct repo names + check payouts."""
import json, urllib.request, urllib.error, urllib.parse, base64

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

# 1) Find the org/repo for the $1,200 Telegram bounty
print("=" * 60)
print("Search for the org behind $1,200 Telegram bounty")
print("=" * 60)
queries = [
    '"Telegram Analytics and Monitoring" is:issue',
    '"$1,200" is:issue',
    '"$1,200" label:bounty',
    'lux is:issue Telegram',
    'HELPDESK.AI is:issue',
    'mergeos is:issue',
    'mergeos bounty MRG',
    'tt-llk RISCV',
]
for q in queries:
    s, d = gh(f"/search/issues?q={urllib.parse.quote(q)}&per_page=5")
    if s == 200:
        items = d.get("items", [])
        if items:
            print(f"  q={q!r}: {len(items)}")
            for it in items[:2]:
                print(f"    #{it.get('number')} {it.get('repository_url','').split('/')[-1]} {it.get('title')[:60]}")
                # Get full body
                repo_url = it.get("repository_url","")
                if repo_url:
                    full = repo_url.replace("https://api.github.com/repos/","")
                    s2, d2 = gh(f"/repos/{full}/issues/{it.get('number')}")
                    if s2 == 200:
                        body = d2.get("body","") or ""
                        # Find payout info
                        if "USDC" in body or "payout" in body.lower() or "address" in body.lower():
                            print(f"      body: {body[:800]}")

# 2) Check the exact URL of HELPDESK.AI bounties
print()
print("=" * 60)
print("HELPDESK.AI repo search")
print("=" * 60)
s, d = gh("/search/repositories?q=HELPDESK-AI&per_page=10")
if s == 200:
    for r in d.get("items",[]):
        print(f"  {r.get('full_name')}: {r.get('description','')[:80]}  ★{r.get('stargazers_count',0)}")

# 3) Find the lux repo
print()
print("=" * 60)
print("lux repo search")
print("=" * 60)
s, d = gh("/search/repositories?q=lux+OR+luxfi&per_page=10")
if s == 200:
    for r in d.get("items",[]):
        print(f"  {r.get('full_name')}: {r.get('description','')[:80]}  ★{r.get('stargazers_count',0)}")

# 4) Check luxfi or luxorg
print()
print("=" * 60)
print("Try specific org names")
print("=" * 60)
for org in ["luxfi","luxorg","luxlabs","lux-ai","LuxNetwork","LuxNetworkAI","luxnetwork","lux-agents","luxai"]:
    s, d = gh(f"/orgs/{org}/repos?per_page=5")
    if s == 200:
        print(f"  {org}: {len(d)} repos")
        for r in d[:3]:
            print(f"    {r.get('full_name')}: {r.get('description','')[:80]}")

# 5) mergeos
print()
print("=" * 60)
print("mergeos repo")
print("=" * 60)
for org in ["mergeos","merge-os","mergeOS","merge-os-labs"]:
    s, d = gh(f"/repos/{org}/{org}")
    if s == 200:
        print(f"  {org}/{org}: {d.get('description','')[:80]}  ★{d.get('stargazers_count',0)}")
    s, d = gh(f"/orgs/{org}/repos?per_page=5")
    if s == 200:
        print(f"  {org}: {len(d)} repos")
        for r in d[:3]:
            print(f"    {r.get('full_name')}: {r.get('description','')[:80]}")
