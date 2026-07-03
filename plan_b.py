#!/usr/bin/env python3
"""Plan B: Make money WITHOUT the user's $150.
Focus on what I can do autonomously:
1. Check existing 3 PRs for activity
2. Find and claim more real-$ bounties
3. Find more discovery platforms
4. Post on X / Show HN / dev.to to drive AIA traffic
5. Check PayanAgent for incoming requests I can fulfill
"""
import os, json, subprocess, urllib.request, ssl, urllib.error, time

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
# 1) CHECK 3 PRs FOR NEW ACTIVITY
# ============================================================
print("=" * 70)
print("1) CHECK 3 PRs FOR NEW ACTIVITY")
print("=" * 70)

for repo, num, bounty, amount in [
    ("cyrilawoyemi99-max/owockibot-bounty-sync-", 37, "owk-004 badges", 400),
    ("cyrilawoyemi99-max/owockibot-bounty-sync-", 39, "owk-005 audit", 1200),
    ("cyrilawoyemi99-max/owockibot-bounty-sync-", 40, "owk-001 dashboard", 750),
]:
    s, _, body = call(f"https://api.github.com/repos/{repo}/pulls/{num}")
    if s == 200:
        j = json.loads(body)
        print(f"\n  PR #{num} ({bounty}, ${amount})")
        print(f"    state: {j.get('state')}, mergeable: {j.get('mergeable')}, merged: {j.get('merged')}")
        print(f"    comments: {j.get('comments')}, review_comments: {j.get('review_comments')}")
        print(f"    updated: {j.get('updated_at')}")
        # Reviews
        s2, _, body2 = call(f"https://api.github.com/repos/{repo}/pulls/{num}/reviews")
        if s2 == 200:
            reviews = json.loads(body2)
            if reviews:
                for r in reviews:
                    print(f"    review: {r.get('state')} by {r.get('user', {}).get('login')}: {r.get('body', '')[:200]}")
            else:
                print(f"    reviews: none yet")
        # Comments (issue style)
        s3, _, body3 = call(f"https://api.github.com/repos/{repo}/issues/{num}/comments")
        if s3 == 200:
            comments = json.loads(body3)
            for c in comments:
                user = c.get("user", {}).get("login", "?")
                if user != "razel369":
                    print(f"    comment by {user}: {c.get('body', '')[:300]}")

# ============================================================
# 2) CHECK OWOCKIBOT BOARD FOR NEW BOUNTIES
# ============================================================
print()
print("=" * 70)
print("2) OWOCKIBOT BOARD - find more bounties")
print("=" * 70)

s, _, body = call("https://owockibot.xyz/api/bounty-board")
if s == 200:
    j = json.loads(body)
    bounties = j if isinstance(j, list) else j.get("bounties", j.get("data", []))
    print(f"  total bounties: {len(bounties)}")
    # Filter open bounties, sort by reward
    open_bounties = [b for b in bounties if b.get("status") == "open" or b.get("claimed_by") in (None, "", "0x0000000000000000000000000000000000000000")]
    open_bounties.sort(key=lambda x: x.get("reward_usdc", 0) or 0, reverse=True)
    print(f"  open bounties: {len(open_bounties)}")
    print(f"\n  TOP 20 OPEN BY REWARD:")
    for b in open_bounties[:20]:
        reward = b.get("reward_usdc", 0)
        if reward < 1: continue  # skip dust
        bid = b.get("id", "?")
        title = b.get("title", "?")[:60]
        claimed = b.get("claimed_by", "")
        claimer = "OPEN" if not claimed or claimed == "0x0000000000000000000000000000000000000000" else f"claimed by {claimed[:10]}"
        print(f"    ${reward:6.2f} | {bid:6} | {title}  ({claimer})")

# ============================================================
# 3) CHECK PAYANAGENT INCOMING REQUESTS
# ============================================================
print()
print("=" * 70)
print("3) PAYANAGENT REQUESTS — find work I can do")
print("=" * 70)

PA_PATH = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\payanagent.json"
with open(PA_PATH) as f:
    pa = json.load(f)
PA_KEY = pa["apiKey"]

s, _, body = call("https://payanagent.com/api/v1/requests?status=open",
                  headers={"Authorization": f"Bearer {PA_KEY}"})
if s == 200:
    j = json.loads(body)
    requests = j.get("requests", [])
    print(f"  open requests: {len(requests)}")
    for r in requests[:10]:
        print(f"    - {r.get('title','?')[:60]}")
        print(f"      budget: {r.get('budget','?')} {r.get('currency','')}")
        print(f"      desc: {r.get('description','')[:200]}")
else:
    print(f"  ERR: {s}")

# Also check all requests (any status)
s, _, body = call("https://payanagent.com/api/v1/requests?limit=50",
                  headers={"Authorization": f"Bearer {PA_KEY}"})
if s == 200:
    j = json.loads(body)
    requests = j.get("requests", [])
    print(f"\n  all requests: {len(requests)}")
    by_status = {}
    for r in requests:
        s_ = r.get("status", "?")
        by_status[s_] = by_status.get(s_, 0) + 1
    print(f"  status breakdown: {by_status}")

# ============================================================
# 4) CDP BAZAAR — search for AIA
# ============================================================
print()
print("=" * 70)
print("4) CDP BAZAAR — search for AIA")
print("=" * 70)

for q in ["aia", "razel369", "rmalka", "Autonomous Insight", "aia-x402", "signal", "news"]:
    s, _, body = call(f"https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?q={q}&limit=20")
    if s == 200:
        items = json.loads(body).get("items", [])
        # Filter for AIA
        aia = [it for it in items if "rmalka" in json.dumps(it).lower() or "aia-x402" in json.dumps(it) or "razel369" in json.dumps(it).lower()]
        if aia:
            print(f"  q={q}: FOUND {len(aia)} AIA entries!")
            for a in aia:
                print(f"    {a.get('resource')}")
        else:
            print(f"  q={q}: {len(items)} items, no AIA match")

# ============================================================
# 5) CHECK PAYANAGENT OFFER VIEWS
# ============================================================
print()
print("=" * 70)
print("5) MY PAYANAGENT OFFERS — views/sales?")
print("=" * 70)

for offer_id in ["kh7fzn8v829swhejta3t81cw7d89t9wx", "kh72mm79gzzd6kzrkepj8jzqs189tks9", "kh7bxn8ce6agc35cd6cz1mr9r589vjc2"]:
    s, _, body = call(f"https://payanagent.com/api/v1/offers/{offer_id}")
    if s == 200:
        j = json.loads(body)
        seller = j.get("seller", {})
        print(f"  {j.get('title','?')[:50]}")
        print(f"    receiptsSold: {seller.get('receiptsSold', 0)}")
        print(f"    totalEarnedCents: {seller.get('totalEarnedCents', 0)}")
        print(f"    reputation: {seller.get('reputation', {})}")

# ============================================================
# 6) CLAWLANCER check
# ============================================================
print()
print("=" * 70)
print("6) CLAWLANCER — recent activity")
print("=" * 70)

s, _, body = call("https://clawlancer.ai/api/listings?listing_type=BOUNTY&status=active&limit=10")
if s == 200:
    j = json.loads(body)
    listings = j.get("listings", [])
    listings.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    print(f"  most recent bounties:")
    for l in listings[:5]:
        print(f"    ${l.get('price_wei', 0)/1e6:.4f} | {l.get('title','?')[:60]}")
