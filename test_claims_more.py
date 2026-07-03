#!/usr/bin/env python3
"""Try multiple Clawlancer bounties + register on PayanAgent + explore OKX AI + look for more platforms."""
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
# 1) TRY 3 DIFFERENT CLAWLANCER BOUNTIES to see if escrow issue is universal
# ============================================================
print("=" * 70)
print("1) CLAIM TEST — multiple bounties")
print("=" * 70)

for bounty_id in [
    "84ffdcc9-f69a-47d6-ae25-9d2e1d91efc7",  # Compare 3 L2 rollups $0.02
    "a0c4c940",  # Survey stablecoin market share $0.025
    "362026ab",  # Regex Ethereum addresses $0.01
    "456c9749",  # Tweet thread agent economies $0.015
]:
    if not bounty_id:
        continue
    if len(bounty_id) == 8:
        # Need full id; look it up
        status, body = call("https://clawlancer.ai/api/listings?listing_type=BOUNTY&status=active&limit=200")
        if status == 200:
            j = json.loads(body)
            for l in j.get("listings", []):
                if l.get("id", "").startswith(bounty_id):
                    bounty_id = l["id"]
                    print(f"  resolved {bounty_id[:8]} -> {l.get('title', '?')[:60]}")
                    break
    status, body = call(
        f"https://clawlancer.ai/api/listings/{bounty_id}/claim",
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    print(f"  claim {bounty_id[:8]}: {status}")
    if status == 200:
        print(f"    ✓ {body[:300]}")
    else:
        # Show the first 200 chars of error
        try:
            j = json.loads(body)
            err = j.get("error", body[:200])
            details = j.get("details", "")
            print(f"    err: {err[:200]}")
            if details: print(f"    details[:300]: {details[:300]}")
        except:
            print(f"    {body[:200]}")

# ============================================================
# 2) PAYANAGENT — register with correct field
# ============================================================
print()
print("=" * 70)
print("2) PAYANAGENT — register with walletAddress")
print("=" * 70)

# Get existing agents
status, body = call("https://payanagent.com/api/v1/agents")
print(f"  GET agents: {status}")
if status == 200:
    j = json.loads(body)
    agents = j if isinstance(j, list) else j.get("agents", [])
    print(f"  existing agents: {len(agents)}")
    for a in agents[:3]:
        print(f"    - {a.get('name', '?')} {a.get('walletAddress', a.get('wallet', '?'))[:20]}")

# Try register with correct field
print()
print("--- Register razel369-aia ---")
status, body = call(
    "https://payanagent.com/api/v1/agents",
    method="POST",
    data={
        "name": "razel369-aia",
        "description": "AIA - Autonomous Insight Agent. Curated multi-source signal stream + x402 paid API. 6 sources, 3 paid endpoints (signals, digest, alerts). 100% autonomous, $0 budget.",
        "walletAddress": WALLET,
        "endpoint": "https://aia-x402.rmalka06.workers.dev",
        "x402Endpoint": "https://aia-x402.rmalka06.workers.dev"
    }
)
print(f"  status: {status}")
print(f"  body: {body[:600]}")
if status in (200, 201):
    j = json.loads(body)
    if "apiKey" in j or "id" in j:
        with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\payanagent.json", "w") as f:
            json.dump(j, f, indent=2)
        print(f"  ✓ saved to payanagent.json")

# Browse all requests
print()
print("--- Browse open requests (work for buyers) ---")
status, body = call("https://payanagent.com/api/v1/requests?status=open")
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    requests = j.get("requests", j if isinstance(j, list) else [])
    print(f"  total open requests: {len(requests)}")
    for r in requests[:10]:
        print(f"    - {r.get('title', '?')[:60]}")
        print(f"      {r.get('description', '?')[:100]}")
        print(f"      budget: {r.get('budget', '?')} {r.get('currency', '')}")

# Browse offers (what other agents sell - I can BUY with x402)
print()
print("--- Browse offers (other agents' services) ---")
status, body = call("https://payanagent.com/api/v1/offers?limit=20")
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    offers = j.get("offers", j if isinstance(j, list) else [])
    print(f"  total offers: {len(offers)}")
    for o in offers[:10]:
        seller = o.get("seller", {})
        print(f"    [{o.get('category', '?')}] {o.get('title', '?')[:50]} - ${o.get('priceUsd', '?')}")
        print(f"        by {seller.get('name', '?')} (score {seller.get('reputation', {}).get('score', '?')})")

# Discover
print()
print("--- Discover (unified search) ---")
for q in ["research", "writing", "data", "agent", "bounty"]:
    status, body = call(f"https://payanagent.com/api/v1/discover?q={q}")
    if status == 200:
        j = json.loads(body)
        if isinstance(j, dict):
            offers = j.get("offers", [])
            requests = j.get("requests", [])
            print(f"  q={q}: {len(offers)} offers, {len(requests)} requests")

# ============================================================
# 3) OKX AI
# ============================================================
print()
print("=" * 70)
print("3) OKX AI")
print("=" * 70)

for path in ["/", "/api", "/api/v1", "/agents", "/api/agents", "/docs", "/api/v1/agents", "/onchainos", "/api/marketplace"]:
    print(f"\n--- https://www.okx.com/ai{path} ---")
    status, body = call(f"https://www.okx.com/ai{path}", timeout=15)
    print(f"  status: {status}")
    print(f"  body[:300]: {body[:300]}")

# Look for the Onchain OS
print()
print("--- Onchain OS / OnchainOS ---")
for path in ["/", "/docs", "/agents", "/skills", "/register"]:
    status, body = call(f"https://onchainos.okx.com{path}", timeout=15)
    print(f"  https://onchainos.okx.com{path}: {status} ({len(body)}b)")
    if status == 200 and "Onchain" in body[:500]:
        print(f"    {body[:300]}")

# GitHub: okx/onchainos-skills
print()
print("--- okx/onchainos-skills on GitHub ---")
r = subprocess.run(["gh","api","repos/okx/onchainos-skills"], capture_output=True, text=True, timeout=20) if False else None
import subprocess
r = subprocess.run(["gh","api","repos/okx/onchainos-skills"], capture_output=True, text=True, timeout=20)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"  ✓ repo exists: {j.get('full_name')}")
    print(f"    description: {j.get('description')}")
    print(f"    stars: {j.get('stargazers_count')}")
    print(f"    default_branch: {j.get('default_branch')}")

# ============================================================
# 4) MORE PLATFORMS
# ============================================================
print()
print("=" * 70)
print("4) MORE PLATFORMS — quick check")
print("=" * 70)

platforms = [
    ("mcp__agentboss", "https://agentboss.ai/api/listings"),
    ("agentropolis", "https://agentropolis.com/api/listings"),
    ("moltlauncher", "https://moltlauncher.xyz/api/listings"),
    ("sherlock", "https://sherlock.xyz/api/audits"),
    ("questflow", "https://questflow.ai/api/quests"),
    ("kleros", "https://kleros.io/api/courts"),
    ("oceanprotocol", "https://market.oceanprotocol.com/api/v1/assets"),
    ("fetchai", "https://agentverse.ai/api/agents"),
    ("autonolas", "https://www.autonolas.network/api/agents"),
    ("singularitynet", "https://marketplace.singularitynet.io/api/v1/services"),
    ("coval", "https://coval.io/api/agents"),
    ("crops", "https://crops.ai/api/jobs"),
    ("kairos", "https://kairos.com/api/marketplace"),
    ("workerd", "https://workerd.app/api/jobs"),
    ("opentask", "https://opentask.io/api/listings"),
    ("agentland", "https://agent.land/api/listings"),
    ("freysa", "https://www.freysa.ai/api"),
    ("truth", "https://truth.bet/api/markets"),
    ("derive", "https://www.derive.xyz/api"),
    ("morpher", "https://www.morpher.com/api"),
    ("agoric", "https://agoric.com/api"),
    ("autonity", "https://autonity.io/api"),
    ("kamino", "https://kamino.finance/api"),
    ("kresko", "https://kresko.io/api"),
]
for name, url in platforms:
    try:
        status, body = call(url, timeout=8)
        ok = "✓" if status in (200, 401, 403) else "?"
        print(f"  {ok} {name}: {status} {url}")
        if status == 200 and "listings" in body.lower():
            print(f"      body: {body[:200]}")
    except Exception as e:
        print(f"  ✗ {name}: ERR {e}")
