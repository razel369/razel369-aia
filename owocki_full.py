#!/usr/bin/env python3
"""Get full owockibot board + find open bounties + check my eligibility."""
import json, urllib.request, urllib.error, re, time

def fetch(url, headers=None):
    h = {"User-Agent":"Mozilla/5.0","Accept":"application/json"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
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

# 1) Full bounty board
print("=" * 60)
print("FULL OWOCKIBOT BOARD")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/bounty-board")
if isinstance(d, list):
    # Group by status
    by_status = {}
    for b in d:
        st = b.get("status","unknown")
        by_status.setdefault(st, []).append(b)
    for st, items in by_status.items():
        print(f"  {st}: {len(items)} bounties")
    print()
    # All bounties sorted by reward desc
    print("  ALL bounties (sorted by reward):")
    for b in sorted(d, key=lambda x: -(x.get("reward_usdc") or 0))[:30]:
        rid = b.get("id")
        title = b.get("title","")[:60]
        reward = b.get("reward_usdc")
        status = b.get("status")
        claimer = b.get("claimer_address","")
        creator = b.get("creator_address","")
        print(f"  #{rid} ${reward} [{status}] {title}")
        if claimer: print(f"    claimer: {claimer[:14]}...")
        if creator: print(f"    creator: {creator[:14]}...")

# 2) Find the open ones
print()
print("=" * 60)
print("OPEN BOUNTIES (claimable now)")
print("=" * 60)
if isinstance(d, list):
    open_b = [b for b in d if b.get("status") == "open"]
    print(f"  open: {len(open_b)}")
    for b in sorted(open_b, key=lambda x: -(x.get("reward_usdc") or 0))[:20]:
        rid = b.get("id")
        title = b.get("title","")
        reward = b.get("reward_usdc")
        desc = b.get("description","")[:200]
        print(f"\n  #{rid} ${reward} {title}")
        print(f"    desc: {desc}")

# 3) Find my recent claims/submissions
print()
print("=" * 60)
print("MY OWOCKIBOT ACTIVITY (wallet 0x833c...3a5e)")
print("=" * 60)
if isinstance(d, list):
    mine = [b for b in d if (b.get("claimer_address") or "").lower().startswith("0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e") or
                              (b.get("creator_address") or "").lower().startswith("0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e")]
    print(f"  my bounties: {len(mine)}")
    for b in mine[:10]:
        print(f"  #{b.get('id')} ${b.get('reward_usdc')} [{b.get('status')}] {b.get('title','')[:60]}")

# 4) Check the API more deeply
print()
print("=" * 60)
print("OWOCKIBOT API SURFACE")
print("=" * 60)
# Try various endpoints
for path in ["/api/bounty-board?status=open", "/api/me", "/api/leaderboard",
             "/api/bounty/413", "/api/bounties/recent", "/api/stats",
             "/api/v1/bounty-board", "/api/treasury", "/api/contract",
             "/api/v1/bounties", "/api/wallet", "/api/users/me"]:
    s, d = fetch(f"https://owockibot.xyz{path}")
    if s == 200:
        if isinstance(d, dict):
            keys = list(d.keys())[:5]
            print(f"  {s} {path}  keys={keys}")
        elif isinstance(d, list):
            print(f"  {s} {path}  list({len(d)})")
        else:
            print(f"  {s} {path}  ({len(d) if isinstance(d,str) else 0}b)")
