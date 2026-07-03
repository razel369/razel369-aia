#!/usr/bin/env python3
"""Analyze all Clawlancer bounties + try to update wallet."""
import json, urllib.request, urllib.error, ssl, os

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

CW_PATH = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\clawlancer.json"
with open(CW_PATH) as f:
    cw = json.load(f)
API_KEY = cw["api_key"]
WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

def call(url, method="GET", data=None, headers=None, timeout=20):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

# ============================================================
# 1) ANALYZE ALL BOUNTIES
# ============================================================
print("=" * 70)
print("1) ALL CLAWLANCER BOUNTIES — by price")
print("=" * 70)

status, body = call("https://clawlancer.ai/api/listings?listing_type=BOUNTY&status=active&sort=newest&limit=200")
if status == 200:
    j = json.loads(body)
    listings = j.get("listings", [])
    bounties = [(l.get("price_wei", 0)/1_000_000, i, l) for i, l in enumerate(listings) if l.get("listing_type") == "BOUNTY"]
    bounties.sort(reverse=True)
    prices = [p for p,_,_ in bounties]
    print(f"  total active bounties: {len(bounties)}")
    print(f"  max price: ${max(prices):.4f}")
    print(f"  min price: ${min(prices):.4f}")
    print(f"  median:    ${sorted(prices)[len(prices)//2]:.4f}")
    print(f"  TOTAL POTENTIAL: ${sum(prices):.4f}")
    print()
    print("  TOP 20 BY PRICE:")
    for price, _, l in bounties[:20]:
        cat = l.get("category", "?")
        title = l.get("title","?")[:70]
        agent = l.get("agent") or {}
        poster = agent.get("name","?")
        print(f"    ${price:.4f} | [{cat:12s}] {title}  ({poster})")

    # Category breakdown
    cats = {}
    for p,_,l in bounties:
        c = l.get("category", "?")
        cats[c] = cats.get(c, 0) + 1
    print()
    print("  CATEGORIES:")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {c}: {n} bounties")

# ============================================================
# 2) UPDATE WALLET — try PATCH
# ============================================================
print()
print("=" * 70)
print("2) PATCH /api/agents/me to set real wallet")
print("=" * 70)

# Try multiple field name variants
for body in [
    {"wallet_address": WALLET, "walletAddress": WALLET},
    {"wallet": WALLET},
    {"wallet_address": WALLET},
    {"walletAddress": WALLET, "bankr_enabled": False, "wallet_provider": "custom"},
]:
    status, resp = call("https://clawlancer.ai/api/agents/me", method="PATCH", data=body,
                        headers={"Authorization": f"Bearer {API_KEY}"})
    print(f"  PATCH with keys={list(body.keys())}: {status} {resp[:300]}")

# Also try PATCH /api/agents/<id>
AGENT_ID = cw["agent"]["id"]
print()
for body in [
    {"wallet_address": WALLET},
    {"walletAddress": WALLET},
    {"wallet": WALLET},
]:
    status, resp = call(f"https://clawlancer.ai/api/agents/{AGENT_ID}", method="PATCH", data=body,
                        headers={"Authorization": f"Bearer {API_KEY}"})
    print(f"  PATCH /api/agents/{AGENT_ID[:8]} with keys={list(body.keys())}: {status} {resp[:300]}")

# GET to see current state
print()
print("--- GET /api/agents/me ---")
status, resp = call("https://clawlancer.ai/api/agents/me",
                    headers={"Authorization": f"Bearer {API_KEY}"})
print(f"  status: {status}")
print(f"  body: {resp[:800]}")

# Re-register with cdp
print()
print("--- Re-register with wallet_provider: cdp ---")
status, resp = call("https://clawlancer.ai/api/agents/register", method="POST",
                    data={"agent_name": "razel369-aia", "wallet_provider": "cdp", "walletAddress": WALLET})
print(f"  status: {status}")
print(f"  body: {resp[:1000]}")
if status in (200, 201):
    j = json.loads(resp)
    if j.get("api_key"):
        # Save new credentials
        with open(CW_PATH, "w") as f:
            json.dump(j, f, indent=2)
        print("  ✓ saved new credentials to clawlancer.json")
        API_KEY = j["api_key"]
