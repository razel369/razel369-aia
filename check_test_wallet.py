#!/usr/bin/env python3
"""Get address from private key, check balances, do test payment to AIA."""
import os, json, time, secrets, hashlib, urllib.request, urllib.error, ssl

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
}

# ============================================================
# 1) DERIVE ADDRESS FROM PRIVATE KEY
# ============================================================
print("=" * 70)
print("1) DERIVE ADDRESS")
print("=" * 70)

from eth_account import Account
PRIVATE_KEY = "0x758ced3b12c9462340867c7f523476f3f9c4d7af08360185b33d5eb224a06bda"
acct = Account.from_key(PRIVATE_KEY)
addr = acct.address
print(f"  Address: {addr}")

# ============================================================
# 2) CHECK BALANCES ON BASE SEPOLIA
# ============================================================
print()
print("=" * 70)
print("2) CHECK BALANCES (BASE SEPOLIA)")
print("=" * 70)

USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
addr_clean = addr[2:].lower().zfill(64)

def rpc(method, params, rpc_url="https://sepolia.base.org"):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc_url, data=payload, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

# ETH balance
r = rpc("eth_getBalance", [addr, "latest"])
if "result" in r:
    bal = int(r["result"], 16) / 1e18
    print(f"  ETH: {bal:.10f}")
else:
    print(f"  ETH: ERR {r}")

# USDC balance
data = "0x70a08231" + addr_clean
r = rpc("eth_call", [{"to": USDC_BASE_SEPOLIA, "data": data}, "latest"])
if "result" in r:
    bal = int(r["result"], 16) / 1e6 if r["result"] != "0x" else 0
    print(f"  USDC: {bal}")
else:
    print(f"  USDC: ERR {r}")

# Nonce
r = rpc("eth_getTransactionCount", [addr, "latest"])
if "result" in r:
    nonce = int(r["result"], 16)
    print(f"  Nonce: {nonce}")
else:
    print(f"  Nonce: ERR {r}")

# Chain ID
r = rpc("eth_chainId", [])
if "result" in r:
    chain_id = int(r["result"], 16)
    print(f"  Chain ID: {chain_id}")
else:
    chain_id = 84532
    print(f"  Chain ID: defaulting to {chain_id}")

# Save wallet info
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\test_wallet.json", "w") as f:
    json.dump({
        "address": addr,
        "private_key": PRIVATE_KEY,
        "chain": "base-sepolia",
        "chain_id": 84532,
        "usdc": USDC_BASE_SEPOLIA,
        "purpose": "x402 test payment to AIA worker"
    }, f, indent=2)
print(f"\n  saved to .agent-credentials/test_wallet.json")
