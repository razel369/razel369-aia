#!/usr/bin/env python3
"""Check balances using multiple Base Sepolia RPCs."""
import json, urllib.request, ssl, urllib.error

ctx = ssl.create_default_context()
HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://chainlist.org"
}

addr = "0xb10871882b12051b5531dBcaf0a564082aB41CeF"
USDC = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
addr_clean = addr[2:].lower().zfill(64)

def rpc(method, params, rpc_url):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc_url, data=payload, method="POST", headers=HEADERS_BROWSER)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:200]}
    except Exception as e:
        return 0, {"error": str(e)}

# Try multiple Sepolia RPCs
RPCS = [
    "https://sepolia.base.org",
    "https://base-sepolia-rpc.publicnode.com",
    "https://base-sepolia.drpc.org",
    "https://1rpc.io/base-sepolia",
    "https://base-sepolia.llamarpc.com",
    "https://base-sepolia.gateway.tenderly.co",
    "https://virtual.base-sepolia.rpc.tenderly.co",
    "https://84532.rpc.thirdweb.com",
    "https://base-sepolia.api.onfinality.io/public",
]

for url in RPCS:
    print(f"\n--- {url} ---")
    # Chain ID
    s, r = rpc("eth_chainId", [], url)
    if s == 200 and "result" in r:
        print(f"  chainId: {int(r['result'], 16)}")

    # Nonce
    s, r = rpc("eth_getTransactionCount", [addr, "latest"], url)
    if s == 200 and "result" in r:
        print(f"  nonce: {int(r['result'], 16)}")

    # ETH balance
    s, r = rpc("eth_getBalance", [addr, "latest"], url)
    if s == 200 and "result" in r:
        print(f"  ETH: {int(r['result'], 16) / 1e18:.10f}")

    # USDC balance
    data = "0x70a08231" + addr_clean
    s, r = rpc("eth_call", [{"to": USDC, "data": data}, "latest"], url)
    if s == 200 and "result" in r:
        bal = int(r["result"], 16) / 1e6 if r["result"] != "0x" else 0
        print(f"  USDC: {bal}")
