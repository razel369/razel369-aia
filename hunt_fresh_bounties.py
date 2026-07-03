#!/usr/bin/env python3
"""Hunt fresh GitHub bounties with no competition.
Criteria:
- Created < 14 days ago
- 0 comments (no competition)
- Has $$ amount + explicit bounty/reward/USDC language
- Issuer is in legit-payer list (or large org)
Uses gh CLI for auth (avoids rate limit)."""
import json, subprocess, re, os, sys
from datetime import datetime, timezone

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

LEGIT_ORGS = [
    "ethereum-optimism", "graphprotocol", "morpho-org", "aave", "lidofinance",
    "uniswap", "euler-xyz", "balancer", "stargate-protocol", "across-protocol",
    "wormhole-foundation", "chainlink", "convex-eth", "yearn-finance",
    "curvefi", "frax-finance", "compound-finance", "synthetix", "rocket-pool",
    "dydxprotocol", "dwebagents", "LayerZero-Labs", "circlefin",
    "ondo-finance", "pendle-finance", "resolv-xyz", "ethereum",
    "bitcoin", "solana-labs", "aptos-labs", "sui-foundation",
    "starknet-io", "scroll-tech", "zksync", "matterlabs",
    "celestiaorg", "cosmos", "osmosis-labs", "injective-protocol",
    "initia-labs", "berachain", "monad-dev", "movementlabsxyz",
    "Manta-Network", "alt-research", "polyhedra-network", "risc0",
    "succinctlabs", "axiom-crypto", "lagrange-labs", "eigenlayer",
    "calderaxyz", "conduit-xyz", "worldcoin", "phala-network",
    "lit-protocol", "mystenlabs", "arbitrum-foundation", "foundry-rs",
    "taikoxyz", "linea-build", "polygon", "avalanche-xyz", "base-org",
    "optimism-pod", "inkonchain", "soneium-xyz", "kakarot",
    "icon-project", "metaplex-foundation", "monad-crypto",
]

def gh_search(query, limit=30):
    """Use gh CLI to search with auth."""
    try:
        result = subprocess.run(
            ["gh", "search", "issues", query, "--limit", str(limit), "--json",
             "number,title,state,repository,url,createdAt,author,comments"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0: return []
        return json.loads(result.stdout)
    except Exception as e:
        return []

def is_fresh(item, days=14):
    try:
        created = datetime.fromisoformat(item["createdAt"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - created).days
        return age <= days
    except: return False

def extract_amount(text):
    if not text: return 0
    amounts = re.findall(r'\$(\d{1,3}(?:,\d{3})*|\d+)\s*(?:k|K|000|USDC|USD)?', text)
    val = 0
    for a in amounts:
        try:
            v = int(a.replace(",", ""))
            if a.lower().endswith("k"):
                v *= 1000
            if 50 <= v <= 1000000:
                val = max(val, v)
        except: pass
    return val

def get_issue_body(repo, number):
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(number), "--repo", repo, "--comments"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout
    except: pass
    return ""

def is_real_bounty(text, title):
    text_l = (text + " " + title).lower()
    has_money = extract_amount(text + " " + title) >= 100
    has_bounty_keyword = any(kw in text_l for kw in [
        "bounty", "reward", "usdc", "usdt", "tip", "compensation", "grant", "paid out", "prize", "incentive"
    ])
    has_work_keyword = any(kw in text_l for kw in [
        "submit", "claim", "fix", "build", "implement", "add", "solve", "complete", "find", "improve", "review", "translate", "design"
    ])
    # Anti-false-positives
    blacklist = ["paper trade", "account snapshot", "buying power", "portfolio value", "submitted buy",
                 "daily-analysis", "github-actions", "auto-generated"]
    if any(b in text_l for b in blacklist):
        return False
    return has_money and has_bounty_keyword and has_work_keyword

def main():
    print(f"\n{'='*70}")
    print(f"FRESH BOUNTY HUNT — {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    found = []

    # 1. Broad search
    print("1. Broad search...")
    broad_queries = [
        "bounty is:open created:>2026-06-20",
        "$500 bounty is:open created:>2026-06-20",
        "usdc reward is:open created:>2026-06-20",
        "label:bounty is:open created:>2026-06-20",
        "is:open \"$\" \"bounty\" created:>2026-06-20",
    ]
    for q in broad_queries:
        items = gh_search(q, limit=20)
        print(f"  Query '{q[:50]}...' returned {len(items)} items")
        for it in items:
            if it.get("state") != "OPEN": continue
            if it.get("comments", 0) > 0: continue
            if not is_fresh(it): continue
            repo = it.get("repository", {}).get("nameWithOwner", "")
            if not repo: continue
            body = get_issue_body(repo, it["number"])
            if not is_real_bounty(body, it.get("title", "")): continue
            amt = extract_amount(it.get("title", "") + " " + body)
            found.append({
                "title": it.get("title", ""),
                "url": it.get("url", ""),
                "amount": amt,
                "comments": it.get("comments", 0),
                "repo": repo,
                "created": it.get("createdAt", ""),
                "author": (it.get("author") or {}).get("login", "")
            })

    # 2. Org-by-org scan (focus on biggest)
    print(f"\n2. Scanning {len(LEGIT_ORGS)} legit orgs...")
    for org in LEGIT_ORGS:
        items = gh_search(f"org:{org} is:open created:>2026-06-15 bounty", limit=10)
        for it in items:
            if it.get("state") != "OPEN": continue
            if it.get("comments", 0) > 2: continue
            if not is_fresh(it): continue
            repo = it.get("repository", {}).get("nameWithOwner", "")
            if not repo: continue
            body = get_issue_body(repo, it["number"])
            if not is_real_bounty(body, it.get("title", "")): continue
            amt = extract_amount(it.get("title", "") + " " + body)
            found.append({
                "title": it.get("title", ""),
                "url": it.get("url", ""),
                "amount": amt,
                "comments": it.get("comments", 0),
                "repo": repo,
                "created": it.get("createdAt", ""),
                "author": (it.get("author") or {}).get("login", "")
            })

    # Dedupe and sort
    seen = set()
    unique = []
    for f in found:
        if f["url"] in seen: continue
        seen.add(f["url"])
        unique.append(f)
    unique.sort(key=lambda x: (-x["amount"], x["comments"]))

    print(f"\n{'='*70}")
    print(f"FOUND {len(unique)} REAL FRESH BOUNTIES")
    print(f"{'='*70}\n")
    for f in unique[:30]:
        print(f"  ${f['amount']:>6}  {f['comments']}c  {f['repo']:40}  by {f['author']}")
        print(f"          {f['title'][:80]}")
        print(f"          {f['url']}")
        print()

    out = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\fresh_bounties.json"
    with open(out, "w") as f:
        json.dump(unique, f, indent=2)
    print(f"Saved to {out}")

if __name__ == "__main__":
    main()
