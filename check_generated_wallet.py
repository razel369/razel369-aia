#!/usr/bin/env python3
"""Check the generated wallet's balances on both chains."""
import json, urllib.request, ssl, urllib.error

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

# This is the wallet I generated
addr = "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2"
PRIVATE_KEY = "0x3f94d512869900c94cc9f0e2d54b203d966a1697e41b04d5d51d8622f0a9e490"

print(f"Wallet: {addr}")
print(f"Private key: {PRIVATE_KEY}")
print()

def blockscout(addr_path, chain):
    url = f"https://{chain}.blockscout.com/api/v2/addresses/{addr_path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:300]}
    except Exception as e:
        return 0, {"error": str(e)}

for chain in ["base", "base-sepolia"]:
    print(f"=== {chain} ===")
    s, r = blockscout(addr, chain)
    if s == 200:
        cb = r.get("coin_balance")
        if cb:
            try:
                cb_int = int(cb, 16) if cb.startswith("0x") else int(cb)
                print(f"  ETH: {cb_int / 1e18:.10f}")
            except: print(f"  ETH raw: {cb}")
        else:
            print(f"  ETH: 0 (no coin_balance field)")
        print(f"  tx count: {r.get('transactions_count')}")
    else:
        print(f"  addr ERR: {s}")

    # Token balances
    s, r = blockscout(f"{addr}/token-balances", chain)
    if s == 200:
        items = r if isinstance(r, list) else r.get("items", [])
        print(f"  token balances: {len(items)}")
        for b in items[:10]:
            tok = b.get("token", {})
            sym = tok.get("symbol", "?")
            decimals = int(tok.get("decimals", 18))
            val = b.get("value", "0")
            if val and val.startswith("0x"):
                val_int = int(val, 16)
            else:
                val_int = int(val) if val else 0
            human = val_int / (10 ** decimals)
            print(f"    {sym}: {human}")
    else:
        print(f"  token-balances ERR: {s}")
    print()

# Also try RPC for nonce
def rpc(method, params, rpc_url):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc_url, data=payload, method="POST", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

for chain_name, rpc_url in [("base", "https://mainnet.base.org"), ("base-sepolia", "https://sepolia.base.org")]:
    r = rpc("eth_getTransactionCount", [addr, "latest"], rpc_url)
    if "result" in r:
        print(f"  {chain_name} nonce: {int(r['result'], 16)}")
