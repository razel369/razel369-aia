#!/usr/bin/env python3
"""Check AIA x402 402 response + try to submit to agentic.market via CDP/API."""
import json, urllib.request, urllib.error, base64, time, subprocess

def fetch(url, headers=None, method="GET", data=None, timeout=20):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e:
        return -1, str(e)

# 1) Check 402 response on AIA Worker
print("=" * 60)
print("AIA 402 RESPONSE (should have bazaar extension)")
print("=" * 60)
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/signals",
             headers={"Accept":"application/json"})
print(f"  status: {s}")
if isinstance(d, dict):
    pr = d.get("paymentRequired") or d.get("payment_required")
    if pr:
        decoded = json.loads(base64.b64decode(pr))
        print(f"  x402Version: {decoded.get('x402Version')}")
        print(f"  accepts[0] keys: {list(decoded.get('accepts',[{}])[0].keys())[:20]}")
        ext = decoded.get("extensions",{})
        print(f"  extensions keys: {list(ext.keys())}")
        bz = ext.get("bazaar",{})
        if bz:
            print(f"  bazaar keys: {list(bz.keys())}")
            svcs = bz.get("services",[])
            print(f"  bazaar services count: {len(svcs)}")
            for s2 in svcs[:3]:
                print(f"    - {s2.get('path','?')}: {s2.get('description','')[:80]}")
    print()
    print(f"  Full 402: {json.dumps(d, indent=2)[:1500]}")

# 2) Try the agentic.market direct API
print()
print("=" * 60)
print("AGENTIC.MARKET: try all endpoints")
print("=" * 60)
endpoints = [
    "https://api.agentic.market/v1/services",
    "https://api.agentic.market/services",
    "https://api.agentic.market/v1/listings",
    "https://api.agentic.market/v1/registry",
    "https://agentic.market/api/v1/services",
]
for u in endpoints:
    s, d = fetch(u, headers={"Accept":"application/json","Origin":"https://agentic.market"})
    print(f"  {s} {u[:80]}")
    if isinstance(d, dict):
        print(f"    keys: {list(d.keys())[:5]}")
    elif isinstance(d, list):
        print(f"    list: {len(d)} items")

# 3) Try posting a service to agentic.market
print()
print("=" * 60)
print("AGENTIC.MARKET: POST a service")
print("=" * 60)
service_payload = {
    "name": "AIA Real-Time Signal Stream",
    "description": "Curated AI/agent/tooling/finance signals from HN, GitHub trending, V2EX, dev.to, Lobsters. Filtered, scored, deduplicated. 40+ items per run.",
    "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
    "price": "0.01",
    "currency": "USDC",
    "network": "base",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "pay_to": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "tags": ["ai","agents","signals","research","hn","github","trending"],
    "outputSchema": {
        "type": "object",
        "properties": {
            "signals": {"type": "array", "items": {"type": "object"}},
            "generated_at": {"type": "string"},
            "source": {"type": "string"}
        }
    }
}
for endpoint in [
    "https://api.agentic.market/v1/services",
    "https://api.agentic.market/services",
    "https://api.agentic.market/v1/listings",
    "https://api.agentic.market/v1/registry/services",
]:
    s, d = fetch(endpoint, method="POST", data=service_payload,
                 headers={"Accept":"application/json","Origin":"https://agentic.market"})
    print(f"  {s} {endpoint}")
    if isinstance(d, dict):
        print(f"    response: {json.dumps(d)[:300]}")
    elif isinstance(d, str):
        print(f"    text: {d[:300]}")
