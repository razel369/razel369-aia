#!/usr/bin/env python3
"""Find easiest-to-win bounties + look at how payouts work + check other ecosystems."""
import json, subprocess, urllib.request, urllib.error

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

# 1) Look at recently COMPLETED bounties to learn what wins
print("=" * 60)
print("RECENTLY COMPLETED OWOCKIBOT BOUNTIES (last 20)")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/bounty-board")
if isinstance(d, list):
    completed = [b for b in d if b.get("status") == "completed"]
    completed.sort(key=lambda x: -(x.get("id") or 0))
    for b in completed[:20]:
        rid = b.get("id")
        title = b.get("title","")[:55]
        reward = b.get("reward_usdc")
        claimer = (b.get("claimer_address") or "")[:14]
        # Get PR link from owk-XXX issue
        body_text = b.get("description","")[:100]
        print(f"  #{rid} ${reward:3d}  {claimer}  {title}")
        print(f"        {body_text}")

# 2) Top earners
print()
print("=" * 60)
print("TOP OWOCKIBOT EARNERS")
print("=" * 60)
if isinstance(d, list):
    earned = {}
    for b in d:
        if b.get("status") == "completed":
            c = (b.get("claimer_address") or "").lower()
            if c:
                earned[c] = earned.get(c, 0) + (b.get("reward_usdc") or 0)
    sorted_e = sorted(earned.items(), key=lambda x: -x[1])
    for addr, amt in sorted_e[:15]:
        print(f"  ${amt:5d}  {addr}")

# 3) Look for VERY recent new bounties (highest IDs)
print()
print("=" * 60)
print("HIGHEST-ID OWOCKIBOT BOUNTIES (newest)")
print("=" * 60)
if isinstance(d, list):
    new_b = sorted(d, key=lambda x: -(x.get("id") or 0))[:15]
    for b in new_b:
        rid = b.get("id")
        title = b.get("title","")[:55]
        reward = b.get("reward_usdc")
        status = b.get("status")
        claimer = (b.get("claimer_address") or "")[:14]
        print(f"  #{rid} ${reward:3d} [{status:10s}] {claimer:14s}  {title}")

# 4) Check if there are 1-week-old cancelled bounties I could re-claim
print()
print("=" * 60)
print("OWK ISSUES — check all bounty IDs 1-20")
print("=" * 60)
for i in range(1, 21):
    issue = gh(f"repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/{i}")
    if isinstance(issue, dict):
        labels = [l.get("name","") for l in issue.get("labels",[])]
        if "owockibot" in labels:
            title = issue.get("title","")[:60]
            print(f"  #{i} {title} ({labels})")
            # Body sample
            body = issue.get("body","")[:300]
            print(f"    {body[:300]}")
