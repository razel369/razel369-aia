#!/usr/bin/env python3
"""Try multiple public Base RPCs to get wallet balance."""
import json, urllib.request, ssl, urllib.error

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

RPCS = [
    "https://mainnet.base.org",
    "https://base.publicnode.com",
    "https://base-rpc.publicnode.com",
    "https://1rpc.io/base",
    "https://base.llamarpc.com",
    "https://base.drpc.org",
]

ctx = ssl.create_default_context()

def call(url, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=payload, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        return json.loads(r.read().decode())

addr_clean = WALLET[2:].lower().zfill(64)
usdc_data = "0x70a08231" + addr_clean
eth_bal_call = [WALLET, "latest"]

print(f"Wallet: {WALLET}")
print()

usdc_found = False
eth_found = False

for rpc in RPCS:
    print(f"--- {rpc} ---")
    # USDC
    try:
        r = call(rpc, "eth_call", [{"to": USDC, "data": usdc_data}, "latest"])
        if "result" in r and r["result"] != "0x":
            bal_int = int(r["result"], 16)
            bal_usdc = bal_int / 1_000_000
            print(f"  USDC: ${bal_usdc:.6f} ({bal_int} raw)")
            usdc_found = True
        else:
            print(f"  USDC: {r}")
    except urllib.error.HTTPError as e:
        print(f"  USDC: HTTP {e.code} - {e.read().decode()[:200]}")
    except Exception as e:
        print(f"  USDC: {type(e).__name__} {e}")

    # ETH
    try:
        r = call(rpc, "eth_getBalance", eth_bal_call)
        if "result" in r:
            bal_int = int(r["result"], 16)
            bal_eth = bal_int / 1e18
            print(f"  ETH:  {bal_eth:.10f} ETH ({bal_int} wei)")
            eth_found = True
        else:
            print(f"  ETH: {r}")
    except urllib.error.HTTPError as e:
        print(f"  ETH: HTTP {e.code} - {e.read().decode()[:200]}")
    except Exception as e:
        print(f"  ETH: {type(e).__name__} {e}")
    print()

# Last block on Base
print("--- Last Base block ---")
for rpc in RPCS:
    try:
        r = call(rpc, "eth_blockNumber", [])
        if "result" in r:
            print(f"  {rpc}: block {int(r['result'], 16)}")
            break
    except:
        continue
