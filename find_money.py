#!/usr/bin/env python3
"""Thorough check of all addresses and find where the money went."""
import json, urllib.request, ssl, urllib.error, hashlib

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

# The key the user sent me in this session
USER_KEY = "0x758ced3b12c9462340867c7f523476f3f9c4d7af08360185b33d5eb224a06bda"

# The wallet I generated earlier
GEN_KEY = "0x3f94d512869900c94cc9f0e2d54b203d966a1697e41b04d5d51d8622f0a9e490"

# The operator wallet
OP_KEY = None  # I don't have this

print("=" * 70)
print("DERIVED ADDRESSES")
print("=" * 70)
from eth_account import Account
u = Account.from_key(USER_KEY)
g = Account.from_key(GEN_KEY)
print(f"  User's key -> 0x{u.address}")
print(f"  My generated key -> 0x{g.address}")
print(f"  Operator (from earlier): 0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e")
print()

# Check all 3 addresses on both chains via Blockscout
addresses = {
    "USER_KEY-derived": u.address,
    "MY-GENERATED": g.address,
    "OPERATOR (no key)": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
}

def blockscout(path, chain):
    url = f"https://{chain}.blockscout.com/api/v2/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as ex:
        return ex.code, {"error": ex.read().decode()[:200]}
    except Exception as e:
        return 0, {"error": str(e)}

for label, addr in addresses.items():
    print(f"=" * 70)
    print(f"{label}: 0x{addr}")
    print(f"=" * 70)

    for chain in ["base-sepolia", "base", "ethereum", "sepolia"]:
        # Address info
        s, r = blockscout(f"addresses/{addr}", chain)
        if s == 200:
            cb = r.get("coin_balance")
            eth = 0
            if cb:
                try:
                    eth = (int(cb, 16) if cb.startswith("0x") else int(cb)) / 1e18
                except: pass
            tx_count = r.get("transactions_count")
            created = r.get("creation_tx_hash") or r.get("creator_address_hash")
            if eth > 0 or tx_count:
                print(f"  [{chain}] ETH={eth:.8f} txs={tx_count} created={created}")

        # Token balances
        s, r = blockscout(f"addresses/{addr}/token-balances", chain)
        if s == 200:
            items = r if isinstance(r, list) else r.get("items", [])
            for b in items:
                tok = b.get("token", {})
                sym = tok.get("symbol", "?")
                decimals = int(tok.get("decimals", 18))
                val = b.get("value", "0")
                if val and val.startswith("0x"):
                    val_int = int(val, 16)
                else:
                    val_int = int(val) if val else 0
                human = val_int / (10 ** decimals)
                if human > 0:
                    print(f"  [{chain}] {sym}: {human}")
    print()

# Also try direct RPC with both addresses on base-sepolia
def rpc(method, params, rpc_url):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc_url, data=payload, method="POST", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        return 0, {"error": str(e)}

print("=" * 70)
print("RPC CHECK (base-sepolia, publicnode.com)")
print("=" * 70)
for label, addr in addresses.items():
    s, r = rpc("eth_getBalance", [addr, "latest"], "https://base-sepolia-rpc.publicnode.com")
    if s == 200 and "result" in r:
        bal = int(r["result"], 16) / 1e18
        print(f"  {label}: 0x{addr}")
        print(f"    ETH: {bal:.10f}")

    # USDC
    USDC_TEST = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    addr_clean = addr[2:].lower().zfill(64)
    s, r = rpc("eth_call", [{"to": USDC_TEST, "data": "0x70a08231" + addr_clean}, "latest"], "https://base-sepolia-rpc.publicnode.com")
    if s == 200 and "result" in r:
        bal = int(r["result"], 16) / 1e6 if r["result"] != "0x" else 0
        if bal > 0:
            print(f"    USDC: {bal}")
