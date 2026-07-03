#!/usr/bin/env python3
"""Start a security audit of The Graph protocol — first serious attempt at $50K+ bug bounty.
Step 1: Find the most likely bug surfaces."""
import os, json, urllib.request, ssl, urllib.error, subprocess, re

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/vnd.github.v3+json",
}

def call(url, method="GET", headers=None, timeout=15):
    h = dict(HEADERS)
    if headers: h.update(headers)
    req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:500]}
    except Exception as e:
        return 0, {"error": str(e)}

# ============================================================
# 1) THE GRAPH — REPOS
# ============================================================
print("=" * 70)
print("1) THE GRAPH - REPOS")
print("=" * 70)

s, j = call("https://api.github.com/orgs/graphprotocol/repos?per_page=100&type=public")
if s == 200:
    repos = j if isinstance(j, list) else []
    print(f"  total repos: {len(repos)}")
    # Find smart contract repos
    sc_repos = []
    for r in repos:
        name = r.get("name", "")
        desc = (r.get("description") or "").lower()
        if any(kw in name.lower() for kw in ["contract", "protocol", "staking", "epoch", "curation", "service", "allocator"]) or \
           any(kw in desc for kw in ["solidity", "contract", "ethereum"]):
            sc_repos.append((name, r.get("stargazers_count", 0), desc[:80]))
    sc_repos.sort(key=lambda x: -x[1])
    print(f"\n  Smart contract repos ({len(sc_repos)}):")
    for name, stars, desc in sc_repos[:20]:
        print(f"    ⭐{stars:5d}  {name}: {desc}")

# ============================================================
# 2) THE GRAPH - SCOPE FROM IMMUNEFI
# ============================================================
print()
print("=" * 70)
print("2) THE GRAPH - IMMUNEFI SCOPE")
print("=" * 70)

text = urllib.request.urlopen("https://r.jina.ai/https://immunefi.com/bug-bounty/thegraph/scope",
                              context=ctx, timeout=30).read().decode()
# Look for in-scope contracts
import re
# Find the scope list
print("  Scope page excerpt:")
print(text[:5000])

# ============================================================
# 3) HIGH-PRIORITY TARGET: The Graph main contracts
# ============================================================
print()
print("=" * 70)
print("3) THE GRAPH - contracts repo contents")
print("=" * 70)

s, j = call("https://api.github.com/repos/graphprotocol/contracts/contents/contracts")
if s == 200:
    items = j if isinstance(j, list) else []
    print(f"  contracts/: {len(items)} items")
    for item in items[:30]:
        print(f"    {item.get('type','?'):4s} {item.get('name','?')}")
