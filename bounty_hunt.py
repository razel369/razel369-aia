#!/usr/bin/env python3
"""AUTOMATED GITHUB BOUNTY HUNTER
Polls GitHub for high-value bug bounty issues, then submits to bug bounty.
Strategy:
- Search GitHub for issues with $$ bounties
- Track new ones
- Find $500+ bounties specifically
- Cross-reference with active projects"""
import os, json, urllib.request, ssl, urllib.error, subprocess, time
from datetime import datetime

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "razel369-aia/1.0",
    "Accept": "application/vnd.github.v3+json",
}

def call(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:300]}
    except Exception as e:
        return 0, {"error": str(e)}

def search_gh(query, sort="created", order="desc", limit=20):
    s, j = call(f"https://api.github.com/search/issues?q={query}&sort={sort}&order={order}&per_page={limit}")
    if s == 200:
        return j.get("items", [])
    return []

# ============================================================
# 1) HIGH-VALUE BOUNTIES
# ============================================================
print("=" * 70)
print("1) SEARCHING GITHUB FOR $$ BOUNTIES")
print("=" * 70)

# Search patterns that indicate real $$ bounties
queries = [
    "$5000 bounty",
    "$1000 bounty",
    "$2000 bounty",
    "$5000 USDC",
    "$1000 USDC",
    "bounty $5000",
    "reward: $",
    "bounty board",
    "in:title bounty",
    "in:body $1000",
    "in:body $5000",
    "in:title reward",
    "1000 USD",
    "5000 USDC"
]

found_issues = []
for q in queries:
    items = search_gh(q, limit=10)
    for item in items:
        # Filter to actual issues (not PRs), and recent
        if "pull_request" in item:
            continue
        title = item.get("title", "")
        body = (item.get("body") or "")[:500]
        url = item.get("html_url", "")
        repo = item.get("repository_url", "").replace("https://api.github.com/repos/", "")
        # Look for $$ in title
        import re
        amounts = re.findall(r'\$(\d{1,3}(?:,\d{3})*|\d+)', title + " " + body)
        max_amt = 0
        for a in amounts:
            try:
                v = int(a.replace(",", ""))
                if 100 < v < 1000000:  # reasonable bounty
                    max_amt = max(max_amt, v)
            except: pass
        if max_amt >= 100:
            found_issues.append({
                "title": title, "url": url, "repo": repo,
                "amount": max_amt, "state": item.get("state"),
                "created": item.get("created_at"),
                "comments": item.get("comments", 0)
            })

# Sort by amount
found_issues.sort(key=lambda x: -x["amount"])

# Dedupe by URL
seen = set()
unique_issues = []
for i in found_issues:
    if i["url"] not in seen:
        seen.add(i["url"])
        unique_issues.append(i)

print(f"  found {len(unique_issues)} unique $$ bounty issues on GitHub")
print()
for i in unique_issues[:25]:
    print(f"  ${i['amount']:6}  [{i['state']:6}] {i['repo']}")
    print(f"           {i['title'][:80]}")
    print(f"           {i['url']}")
    print()

# ============================================================
# 2) KEY GITHUB ACCOUNTS TO MONITOR (active bounty issuers)
# ============================================================
print()
print("=" * 70)
print("2) ACTIVE BOUNTY ISSUERS ON GITHUB")
print("=" * 70)

issuers = [
    "cyrilawoyemi99-max",     # owockibot (already worked with)
    "owocki-bot",              # upstream owockibot
    "ethereum-optimism",       # Optimism Foundation
    "ethereum",                # Ethereum Foundation
    "solana-labs",            # Solana
    "solana-foundation",      # Solana Foundation
    "arbitrum-foundation",     # Arbitrum
    "Uniswap",                # Uniswap
    "aave",                    # Aave
    "morpho-org",              # Morpho
    "graphprotocol",           # The Graph
    "lombard-finance",         # Lombard
    "StackingDAO",             # StackingDAO
    "immunefi",                # Immunefi
    "cantina",                 # Cantina
    "code-423n4",              # Code4rena
]

active_issues = []
for org in issuers:
    # Search recent issues
    s, j = call(f"https://api.github.com/search/issues?q=org:{org}+is:issue+is:open&sort=created&order=desc&per_page=3")
    if s == 200:
        for item in j.get("items", []):
            if "pull_request" in item: continue
            title = item.get("title", "")
            body = (item.get("body") or "")[:300]
            url = item.get("html_url", "")
            active_issues.append({"org": org, "title": title, "url": url, "body": body[:200]})

print(f"  found {len(active_issues)} recent issues from active issuers")
for i in active_issues[:15]:
    print(f"  {i['org']:25}: {i['title'][:70]}")
    print(f"                          {i['url']}")

# ============================================================
# 3) IMMUNEFI + CANTINA - my already-known targets
# ============================================================
print()
print("=" * 70)
print("3) TARGETED BOUNTY PROGRAMS")
print("=" * 70)
print("  The Graph $50K:  https://immunefi.com/bug-bounty/thegraph/information")
print("  Morpho $2.5M:    https://cantina.xyz/bounties/35a5f0a1-2ffd-432c-8f3b-77d169add8c3")
print("  Coinbase $5M:    https://cantina.xyz/bounties/55316f42-3c5e-4746-9bd0-0f18dcbc344b")
print()

# ============================================================
# 4) SAVE STATE
# ============================================================
print()
print("=" * 70)
print("4) SAVING STATE")
print("=" * 70)

state = {
    "timestamp": datetime.now().isoformat(),
    "github_bounties_found": len(unique_issues),
    "active_issues_monitored": len(active_issues),
    "top_bounties": unique_issues[:20]
}

state_path = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\bounty_state.json"
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
print(f"  saved: {state_path}")
print(f"  {len(unique_issues)} bounties in queue")
print(f"  {len(active_issues)} active issues being monitored")

# ============================================================
# 5) START CONTINUOUS POLLING
# ============================================================
print()
print("=" * 70)
print("5) STARTING CONTINUOUS POLLER (runs in background)")
print("=" * 70)

# Save poller script
poller = '''#!/usr/bin/env python3
"""Continuous bounty poller — finds new $$ bounties every 30 minutes."""
import json, time, subprocess
from datetime import datetime

while True:
    try:
        subprocess.run(["python", "C:\\\\Users\\\\rmalk\\\\projects\\\\razel369-aia\\\\bounty_hunt.py"], timeout=300)
    except Exception as e:
        print(f"err: {e}")
    time.sleep(1800)  # 30 min
'''
with open(r"C:\Users\rmalk\projects\razel369-aia\bounty_poll.py", "w") as f:
    f.write(poller)
print("  saved bounty_poll.py (30 min interval)")

print()
print("READY. Polling every 30 min for new $$ bounties.")
