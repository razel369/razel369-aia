#!/usr/bin/env python3
"""Continuous bounty monitor — runs in background, alerts on $$ opportunities.
Watches: GitHub issues, Immunefi programs, Cantina contests, Code4rena.
Output: prints to stdout, saves to bounty_state.json every cycle."""
import json, time, subprocess, os, re, urllib.request, ssl, urllib.error
from datetime import datetime

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {"User-Agent": "razel369-aia/1.0", "Accept": "application/vnd.github.v3+json"}
STATE_PATH = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\bounty_state.json"

def gh_search(query, limit=20):
    try:
        url = f"https://api.github.com/search/issues?q={query}&sort=created&order=desc&per_page={limit}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            return json.loads(r.read().decode()).get("items", [])
    except Exception as e:
        return []

def check_immunefi_programs():
    """Parse Immunefi explore page for new programs."""
    try:
        text = urllib.request.urlopen("https://r.jina.ai/https://immunefi.com/explore", context=ctx, timeout=30).read().decode()
        # Count programs
        count = text.count("bug-bounty/")
        return {"immunefi_total_programs": count}
    except: return {}

def check_cantina():
    try:
        text = urllib.request.urlopen("https://r.jina.ai/https://cantina.xyz/opportunities/bounties", context=ctx, timeout=30).read().decode()
        bounties = re.findall(r'\$([0-9,]+)\s*in\s*USDC', text)
        return {"cantina_bounties_total": sum(int(b.replace(",", "")) for b in bounties[:10])}
    except: return {}

def find_bounties():
    found = []
    queries = [
        "$5000 bounty is:open",
        "$10000 bounty is:open",
        "$1000 USDC is:open",
        "$5000 USDC is:open",
        "bounty board is:open",
        "bounty rewards is:open",
        "label:bounty is:open",
        "label:\"bug bounty\" is:open"
    ]
    for q in queries:
        items = gh_search(q, limit=5)
        for item in items:
            if "pull_request" in item: continue
            title = item.get("title", "")
            body = (item.get("body") or "")[:500]
            amounts = re.findall(r'\$(\d{1,3}(?:,\d{3})*|\d+)', title + " " + body)
            max_amt = 0
            for a in amounts:
                try:
                    v = int(a.replace(",", ""))
                    if 100 < v < 1000000:
                        max_amt = max(max_amt, v)
                except: pass
            if max_amt >= 100:
                found.append({
                    "title": title,
                    "url": item.get("html_url", ""),
                    "amount": max_amt,
                    "state": item.get("state"),
                    "created": item.get("created_at"),
                    "repo": item.get("repository_url", "").replace("https://api.github.com/repos/", "")
                })
    # Dedupe
    seen = set()
    unique = []
    for f in found:
        if f["url"] not in seen:
            seen.add(f["url"])
            unique.append(f)
    unique.sort(key=lambda x: -x["amount"])
    return unique

# Main loop
print(f"\n{'='*60}\nBOUNTY MONITOR — {datetime.now().isoformat()}\n{'='*60}\n")

while True:
    bounties = find_bounties()
    immu = check_immunefi_programs()
    cantina = check_cantina()

    state = {
        "timestamp": datetime.now().isoformat(),
        "github_bounties_found": len(bounties),
        "top_10": bounties[:10],
        **immu,
        **cantina
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] github={len(bounties)} | "
          f"immunefi={state.get('immunefi_total_programs', '?')} | "
          f"cantina=${state.get('cantina_bounties_total', '?')}")
    for b in bounties[:5]:
        print(f"  ${b['amount']:6}  {b['title'][:80]}")

    print()
    print("Sleeping 30 min until next poll...")
    time.sleep(1800)
