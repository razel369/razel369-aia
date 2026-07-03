#!/usr/bin/env python3
"""Register AIA on Clawlancer, PayanAgent, OKX AI + check discovery."""
import json, urllib.request, urllib.error, ssl

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

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
# 1) CLAWLANCER
# ============================================================
print("=" * 70)
print("1) CLAWLANCER — clawlancer.ai")
print("=" * 70)

# Register
print("--- Register agent ---")
status, body = call(
    "https://clawlancer.ai/api/agents/register",
    method="POST",
    data={"agent_name": "razel369-aia"}
)
print(f"  status: {status}")
print(f"  body: {body[:1000]}")
if status in (200, 201):
    j = json.loads(body)
    agent_id = j.get("agent_id")
    api_key = j.get("api_key")
    print(f"  ✓ REGISTERED")
    print(f"  agent_id: {agent_id}")
    print(f"  api_key: {api_key[:20]}..." if api_key else "  api_key: NONE")
    if api_key:
        # Save
        with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\clawlancer.json", "w") as f:
            json.dump(j, f, indent=2)
        print("  saved to clawlancer.json")

# Browse bounties
print()
print("--- Browse bounties (any) ---")
status, body = call("https://clawlancer.ai/api/listings?listing_type=BOUNTY")
print(f"  status: {status}")
print(f"  body: {body[:1500]}")

# Browse all
print()
print("--- Browse ALL listings ---")
status, body = call("https://clawlancer.ai/api/listings")
print(f"  status: {status}")
print(f"  body: {body[:1500]}")

# ============================================================
# 2) PAYANAGENT
# ============================================================
print()
print("=" * 70)
print("2) PAYANAGENT — payanagent.com / github derNif/payanagent")
print("=" * 70)

# Check the hosted instance
print("--- Discover ---")
status, body = call("https://payanagent.com/api/v1/discover")
print(f"  status: {status}")
print(f"  body[:600]: {body[:600]}")

# Register
print()
print("--- Register agent ---")
status, body = call(
    "https://payanagent.com/api/v1/agents",
    method="POST",
    data={
        "name": "razel369-aia",
        "description": "AIA - Autonomous Insight Agent. Curated multi-source signal stream + x402 paid API. 6 sources, 3 paid endpoints (signals, digest, alerts).",
        "wallet": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
        "endpoint": "https://aia-x402.rmalka06.workers.dev",
        "x402_endpoint": "https://aia-x402.rmalka06.workers.dev"
    }
)
print(f"  status: {status}")
print(f"  body: {body[:1000]}")
if status in (200, 201):
    j = json.loads(body)
    print(f"  ✓ REGISTERED: {j}")

# Browse offers
print()
print("--- Browse offers ---")
status, body = call("https://payanagent.com/api/v1/offers")
print(f"  status: {status}")
print(f"  body[:1000]: {body[:1000]}")

# Browse requests
print()
print("--- Browse requests ---")
status, body = call("https://payanagent.com/api/v1/requests")
print(f"  status: {status}")
print(f"  body[:1000]: {body[:1000]}")

# ============================================================
# 3) 402SCAN — check if AIA is listed
# ============================================================
print()
print("=" * 70)
print("3) 402SCAN — search for AIA")
print("=" * 70)

# x402scan search
for q in ["aia", "razel369", "Autonomous Insight Agent", "signals"]:
    print(f"\n--- q={q} ---")
    status, body = call(f"https://www.x402scan.com/api/search?q={q}")
    print(f"  status: {status}")
    print(f"  body[:500]: {body[:500]}")

# Try the api/v1 path
for path in ["/api/services", "/api/v1/services", "/services"]:
    print(f"\n--- {path} ---")
    status, body = call(f"https://www.x402scan.com{path}")
    print(f"  status: {status}")
    print(f"  body[:400]: {body[:400]}")

# ============================================================
# 4) AGENTIC.MARKET
# ============================================================
print()
print("=" * 70)
print("4) AGENTIC.MARKET")
print("=" * 70)

for path in ["/", "/api/services", "/api", "/api/v1/services", "/discover"]:
    print(f"\n--- https://agentic.market{path} ---")
    status, body = call(f"https://agentic.market{path}")
    print(f"  status: {status}")
    print(f"  body[:300]: {body[:300]}")
