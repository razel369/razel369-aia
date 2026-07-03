#!/usr/bin/env python3
"""Investigate the best owockibot bounties and find the numbered ones (owk-002 etc)."""
import os, json, subprocess, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

def call(url, method="GET", data=None, headers=None, timeout=30):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        if isinstance(data, dict): data = json.dumps(data)
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()
    except Exception as e:
        return 0, {}, str(e)

# ============================================================
# 1) Get owk-002 to owk-010 from the issue tracker
# ============================================================
print("=" * 70)
print("1) FIND NUMBERED BOUNTIES (owk-002, owk-003, owk-006 etc)")
print("=" * 70)

# Use gh to find issues
r = subprocess.run(["gh","issue","list","--repo","cyrilawoyemi99-max/owockibot-bounty-sync-",
                    "--state","all","--limit","50","--json","number,title,state,labels,url,createdAt,comments"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"  total issues: {len(j)}")
    for issue in j:
        n = issue.get("number")
        t = issue.get("title", "")
        s = issue.get("state", "")
        labels = [l.get("name","") for l in issue.get("labels", [])]
        comments = issue.get("comments", 0)
        if "owk" in t.lower() or "bounty" in t.lower() or any("bounty" in l.lower() for l in labels):
            print(f"  #{n}: {t}  state={s}  comments={comments}  labels={labels}")
            print(f"        url: {issue.get('url')}")
else:
    print(f"  ERR: {r.stderr[:300]}")

# ============================================================
# 2) Get details on the 3 highest-value REAL bounties
# ============================================================
print()
print("=" * 70)
print("2) DETAILS on high-value bounties")
print("=" * 70)

s, _, body = call("https://owockibot.xyz/api/bounty-board")
if s == 200:
    j = json.loads(body)
    bounties = j if isinstance(j, list) else []
    # Filter to $40+ (avoid dust)
    high_value = [b for b in bounties if (b.get("reward_usdc") or 0) >= 40]
    high_value.sort(key=lambda x: x.get("reward_usdc", 0), reverse=True)
    print(f"  bounties worth $40+: {len(high_value)}")
    for b in high_value[:15]:
        bid = b.get("id", "?")
        title = b.get("title", "?")
        reward = b.get("reward_usdc", 0)
        claimed = b.get("claimed_by", "")
        desc = b.get("description", "")[:200]
        if reward >= 999: continue  # skip scam
        print(f"\n  #{bid} - ${reward} USDC - {title}")
        print(f"    claimed: {'OPEN' if not claimed else claimed[:14]+'...'}")
        print(f"    desc: {desc[:200]}")

# ============================================================
# 3) Look at the owk-002, owk-003 numbered bounties specifically
# ============================================================
print()
print("=" * 70)
print("3) owk-002, owk-003, owk-006 SPECIFIC ISSUES")
print("=" * 70)

# Get all issues with "owk" in title
r = subprocess.run(["gh","issue","list","--repo","cyrilawoyemi99-max/owockibot-bounty-sync-",
                    "--state","all","--limit","100","--json","number,title,state,body,labels,comments,url"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    j = json.loads(r.stdout)
    for issue in j:
        t = issue.get("title", "")
        n = issue.get("number", 0)
        if "owk-002" in t or "owk-003" in t or "owk-004" in t or "owk-005" in t or "owk-006" in t or "owk-007" in t or "owk-008" in t or "owk-009" in t or "owk-010" in t or "owk-011" in t or "owk-012" in t:
            print(f"\n  #{n}: {t}")
            print(f"    state: {issue.get('state')}")
            body = issue.get("body", "")[:500]
            print(f"    body: {body}")

# ============================================================
# 4) Check $999M scam - is it real?
# ============================================================
print()
print("=" * 70)
print("4) #180 huge bounty")
print("=" * 70)

s, _, body = call("https://owockibot.xyz/api/bounty/180")
print(f"  /api/bounty/180: {s}")
print(f"  body: {body[:1000]}")

# ============================================================
# 5) Look at owk-001 in more detail (to see what others are submitting)
# ============================================================
print()
print("=" * 70)
print("5) owk-001 (#1) - see existing PRs as competition")
print("=" * 70)

r = subprocess.run(["gh","pr","list","--repo","cyrilawoyemi99-max/owockibot-bounty-sync-",
                    "--state","all","--limit","20","--json","number,title,state,additions,createdAt,url,author"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"  total PRs: {len(j)}")
    for p in j:
        print(f"  #{p.get('number')}: {p.get('title','')[:80]}  state={p.get('state')}  by {p.get('author',{}).get('login')}")
        print(f"        +{p.get('additions')} lines | created {p.get('createdAt')}")
        print(f"        url: {p.get('url')}")
