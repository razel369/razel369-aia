#!/usr/bin/env python3
"""Test new 402 response + find testnet USDC faucet."""
import json, urllib.request, ssl, urllib.error, os, re

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
}

def call(url, method="GET", data=None, headers=None, timeout=20):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        if isinstance(data, dict): data = json.dumps(data)
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()
    except Exception as e:
        return 0, {}, str(e)

# ============================================================
# 1) TEST NEW 402 RESPONSE
# ============================================================
print("=" * 70)
print("1) TEST 402 RESPONSE — /v1/signals")
print("=" * 70)

status, headers, body = call("https://aia-x402.rmalka06.workers.dev/v1/signals", headers={"Accept": "application/json"})
print(f"  status: {status}")
print(f"  content-type: {headers.get('content-type', '?')}")
pr_header = headers.get("PAYMENT-REQUIRED") or headers.get("payment-required")
if pr_header:
    import base64
    decoded = base64.b64decode(pr_header).decode("utf-8")
    j = json.loads(decoded)
    print()
    print("  PAYMENT-REQUIRED decoded:")
    print(json.dumps(j, indent=2)[:2000])
else:
    print(f"  no PAYMENT-REQUIRED header")
    print(f"  body: {body[:500]}")

# ============================================================
# 2) Health check
# ============================================================
print()
print("=" * 70)
print("2) /health")
print("=" * 70)
status, _, body = call("https://aia-x402.rmalka06.workers.dev/health")
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    print(f"  ok={j.get('ok')}")
    print(f"  cdp_facilitator: {j.get('cdp_facilitator')}")
    print(f"  fallback_facilitator: {j.get('fallback_facilitator')}")
    print(f"  routes:")
    for r in j.get("routes", []):
        print(f"    {r.get('path')}: {r.get('price')} {r.get('description')[:60]}")

# ============================================================
# 3) Test CDP facilitator (does it exist?)
# ============================================================
print()
print("=" * 70)
print("3) TEST CDP FACILITATOR endpoints")
print("=" * 70)

for path in ["/platform/v2/x402", "/platform/v2/x402/verify", "/platform/v2/x402/settle", "/platform/v2/x402/discovery/resources"]:
    url = f"https://api.cdp.coinbase.com{path}"
    status, _, body = call(url, method="POST" if path.endswith(("verify","settle")) else "GET",
                            data={"x402Version": 2, "paymentPayload": {}, "paymentRequirements": {}} if "verify" in path or "settle" in path else None)
    print(f"  {url}: {status} ({len(body)}b)")
    if status != 200 or len(body) < 200:
        print(f"    {body[:300]}")

# ============================================================
# 4) Base Sepolia USDC faucet — try CDP one and others
# ============================================================
print()
print("=" * 70)
print("4) BASE SEPOLIA USDC FAUCET")
print("=" * 70)

# Try Circle's official testnet faucet
print("\n--- Circle Faucet ---")
for url in [
    "https://faucet.circle.com/api/v1/faucet/claim",
    "https://faucet.circle.com/api/faucet",
    "https://faucet.circle.com",
]:
    status, _, body = call(url, method="POST",
                            data={"address": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e", "chain": "base-sepolia"},
                            headers={"Content-Type": "application/json"})
    print(f"  POST {url}: {status} ({len(body)}b)")
    print(f"    {body[:300]}")

# Try CDP's faucet (Coinbase Developer Platform)
print("\n--- Coinbase CDP Faucet ---")
for url in [
    "https://api.cdp.coinbase.com/platform/v2/faucet",
    "https://api.cdp.coinbase.com/platform/v2/faucet/claim",
    "https://api.developer.coinbase.com/faucet",
    "https://faucet.developer.coinbase.com",
]:
    status, _, body = call(url, method="POST",
                            data={"address": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e", "network": "base-sepolia"},
                            headers={"Content-Type": "application/json"})
    print(f"  POST {url}: {status} ({len(body)}b)")
    print(f"    {body[:300]}")

# Try thirdweb Base Sepolia faucet
print("\n--- thirdweb Base Sepolia ---")
status, _, body = call("https://thirdweb.com/base-sepolia-faucet", timeout=20)
print(f"  GET: {status} ({len(body)}b)")

# Try cloudfront / Google Cloud web3 faucet
for url in [
    "https://cloud.google.com/application/web3/faucet/ethereum/base-sepolia",
    "https://www.alchemy.com/faucets/base-sepolia",
]:
    print(f"\n  --- {url} ---")
    status, _, body = call(url, timeout=15)
    print(f"  GET: {status} ({len(body)}b)")

# 5) Check our operator wallet on Base Sepolia (nonce 0 means never used)
print()
print("--- Operator wallet on Base Sepolia ---")
WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC_TEST = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
addr_clean = WALLET[2:].lower().zfill(64)

# Try multiple public RPCs for Base Sepolia
for rpc in ["https://sepolia.base.org", "https://base-sepolia-rpc.publicnode.com", "https://base-sepolia.drpc.org"]:
    print(f"\n  {rpc}")
    # Nonce
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionCount", "params": [WALLET, "latest"]}
    status, _, body = call(rpc, method="POST", data=payload,
                            headers={"Content-Type": "application/json"}, timeout=10)
    if status == 200:
        j = json.loads(body)
        nonce = int(j.get("result", "0x0"), 16) if j.get("result") else 0
        print(f"    nonce: {nonce}")

    # USDC balance
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": USDC_TEST, "data": "0x70a08231" + addr_clean}, "latest"]}
    status, _, body = call(rpc, method="POST", data=payload,
                            headers={"Content-Type": "application/json"}, timeout=10)
    if status == 200:
        j = json.loads(body)
        result = j.get("result", "0x0")
        bal = int(result, 16) if result and result != "0x" else 0
        print(f"    USDC (testnet): {bal / 1e6}")
