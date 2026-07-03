#!/usr/bin/env python3
"""Search GitHub for active GitGrant /bounty USDC issues."""
import json, subprocess

def gh_search(query, state="open", limit=30):
    r = subprocess.run(["gh","search","issues",query,"--state",state,"--limit",str(limit),
                        "--json","number,title,url,repository,body,commentsCount,author,labels"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return []
    try: return json.loads(r.stdout)
    except: return []

# Search various bounty patterns
queries = [
    "/bounty USDC",
    "/bounty $",
    "Bounty: USDC",
    "bounty: $100 USDC",
    "Bounty: 50 USDC",
    "$ USDC paid on merge",
    "bounty-bot USDC",
    "BountyEscrow USDC",
]

for q in queries:
    results = gh_search(q, limit=15)
    if results:
        print(f"\n=== q='{q}' ({len(results)} results) ===")
        for r in results[:10]:
            repo = r.get("repository",{}).get("nameWithOwner","?")
            num = r.get("number")
            title = r.get("title","")
            url = r.get("url","")
            body = (r.get("body","") or "")[:200].replace("\n"," ")
            print(f"  {repo}#{num}: {title[:60]}")
            print(f"    url: {url}")
            print(f"    body: {body}")
