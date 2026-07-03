#!/usr/bin/env python3
"""Look for weekly bounties + check owockibot xyz for latest bounties + look at builder category."""
import json, urllib.request, urllib.error, re, subprocess, os

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except Exception as e: return -1, str(e)

# 1) Find weekly bounties in owockibot
print("=" * 60)
print("OWOCKIBOT: weekly bounties")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/bounty-board")
if isinstance(d, list):
    weekly = [b for b in d if "WEEKLY" in (b.get("title","") or "").upper() or "week" in (b.get("title","") or "").lower()]
    weekly.sort(key=lambda x: -(x.get("id") or 0))
    print(f"  weekly bounties: {len(weekly)}")
    for b in weekly[:15]:
        print(f"  #{b.get('id')} ${b.get('reward_usdc')} [{b.get('status')}] {b.get('title','')[:80]}")

# 2) Check owockibot.xyz builder category for new bounties
print()
print("=" * 60)
print("OWOCKIBOT.XYZ: builder + ecological + recent activity")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/")
if isinstance(d, str):
    # Find all bounty IDs
    ids = set()
    for m in re.finditer(r'/bounty/(\d+)', d):
        ids.add(int(m.group(1)))
    for m in re.finditer(r'#(\d{2,4})', d):
        try: ids.add(int(m.group(1)))
        except: pass
    print(f"  bounty IDs on homepage: {sorted(ids)[:20]}")
    # Look for "Builder" / "Ecological"
    for cat in ["Builder", "Ecological", "Engineering", "Translation", "Content", "Design", "Security"]:
        cnt = len(re.findall(rf"\b{cat}\b", d))
        if cnt > 0: print(f"  '{cat}': {cnt} mentions")
    # Find links to specific bounties
    for m in re.finditer(r'href="(/bounty/(\d+)[^"]*)"', d):
        print(f"  link: {m.group(1)}")

# 3) Check the current week's bounty on GitHub tracker
print()
print("=" * 60)
print("OWOCKIBOT GitHub issues — current week bounties")
print("=" * 60)
# Look at recent issues in the mirror repo
r = subprocess.run(["gh","api","repos/cyrilawoyemi99-max/owockibot-bounty-sync-/issues?state=open&per_page=30"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: issues = json.loads(r.stdout)
    except: issues = []
    for i in issues[:15]:
        if "owockibot" in [l.get("name","") for l in i.get("labels",[])]:
            title = i.get("title","")[:60]
            num = i.get("number")
            print(f"  #{num} {title}")

# 4) Check if the 4 week-old claimed bounties are still alive (may expire soon)
print()
print("=" * 60)
print("OWOCKIBOT: claimed bounties age")
print("=" * 60)
if isinstance(d, list):
    for b in d:
        st = b.get("status")
        if st == "claimed":
            print(f"  #{b.get('id')} ${b.get('reward_usdc')} {b.get('title','')[:60]}")
            print(f"    claimer: {(b.get('claimer_address') or '')[:14]}")

# 5) Try posting on the issue tracker to get noticed
print()
print("=" * 60)
print("GITHUB: see if maintainer has any public DMs or contact")
print("=" * 60)
# Check profile of owner
r = subprocess.run(["gh","api","users/cyrilawoyemi99-max","--jq",".bio"],
                   capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    print(f"  bio: {r.stdout[:300]}")
r = subprocess.run(["gh","api","users/cyrilawoyemi99-max","--jq",".twitter_username"],
                   capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    print(f"  twitter: {r.stdout.strip()}")
r = subprocess.run(["gh","api","users/cyrilawoyemi99-max","--jq",".blog"],
                   capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    print(f"  blog: {r.stdout.strip()}")
