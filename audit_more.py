#!/usr/bin/env python3
"""Look for owk-005 vulnerabilities + check owockibot new bounties + read server.js routes."""
import subprocess, json, base64, urllib.request, urllib.error

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except Exception as e: return -1, str(e)

# 1) Get full server.js (it was 96k chars, save it)
content = None
r = subprocess.run(["gh","api","repos/owocki-bot/ai-bounty-board/contents/server.js"], capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try:
        j = json.loads(r.stdout)
        content = base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
    except: pass

if content:
    # Save to file
    with open(r"C:\Users\rmalk\projects\razel369-aia\server_full.js", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved server.js: {len(content)} chars")
    # Look at the routes
    import re
    routes = re.findall(r"app\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]", content)
    print(f"\n  Routes found: {len(routes)}")
    for method, path in routes[:30]:
        print(f"    {method.upper():6s} {path}")
    # Look for auth checks
    print()
    print("  Auth-related keywords:")
    for kw in ["auth", "isMod", "signature", "verify", "wallet", "x-payment", "x402"]:
        cnt = len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
        print(f"    {kw}: {cnt} mentions")
    # Look at the submit/claim/approve routes
    print()
    print("  Submit/claim/approve handlers:")
    for method, path in routes:
        if any(kw in path.lower() for kw in ["submit", "claim", "approve", "cancel", "release", "create"]):
            print(f"    {method.upper():6s} {path}")

# 2) Check owockibot.xyz for new bounties
print()
print("=" * 60)
print("OWOCKIBOT XYZ: full board look")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/bounty-board")
if isinstance(d, list):
    # Find any new ones in last 24h
    # We don't have created_at in API, but check open + recent
    by_status = {}
    for b in d:
        st = b.get("status","unknown")
        by_status.setdefault(st, []).append(b)
    for st, items in sorted(by_status.items()):
        print(f"  {st}: {len(items)}")
    # List "open" by id
    open_b = [b for b in d if b.get("status") == "open"]
    print(f"\n  OPEN bounties: {len(open_b)}")
    for b in open_b:
        print(f"  #{b.get('id')} ${b.get('reward_usdc')} {b.get('title','')[:60]}")

# 3) Check owockibot xyz for builder/ecological categories
print()
print("=" * 60)
print("OWOCKIBOT.XYZ homepage — new bounties?")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/")
if isinstance(d, str):
    # Find recent bounty references
    bounty_refs = set()
    for m in re.finditer(r'/bounty/(\d+)', d):
        bounty_refs.add(m.group(1))
    print(f"  bounty IDs in homepage: {sorted([int(x) for x in bounty_refs])[:20]}")
    # Look for "NEW" labels
    if "new" in d.lower():
        print("  has 'new' labels")
    # Look for "Builder" / "Ecological" category
    for cat in ["Builder", "Ecological", "Engineering", "Design", "Content", "Translation", "Security"]:
        if cat in d:
            print(f"  has '{cat}' category")

# 4) Find the new bounties from the activity feed
print()
print("=" * 60)
print("OWOCKIBOT recent activity (find new bounties)")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/activity")
if s == 200:
    print(f"  activity: {json.dumps(d)[:500]}")
else:
    # Try other paths
    for path in ["/api/recent", "/api/feed", "/api/bounties/recent", "/api/v1/activity"]:
        s, d = fetch(f"https://owockibot.xyz{path}")
        if s == 200:
            print(f"  {s} {path}: {json.dumps(d)[:500]}")
            break
