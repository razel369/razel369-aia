#!/usr/bin/env python3
"""Save the new key, check its address, restart the watcher for BOTH wallets."""
import os, json, time, urllib.request, ssl, urllib.error, base64, secrets, sys

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

NEW_KEY = "0xb833d9773642fa746fa22484eac8f82fa4dca6e87532d0bce23cfc3be094b06d"

# Derive address
from eth_account import Account
acct = Account.from_key(NEW_KEY)
print(f"NEW KEY address: {acct.address}")
print(f"OPERATOR expected: 0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e")
print(f"D32A expected: 0xD32A3a5E29eeb37f2A95a8617013438afffA00E2")
print(f"MATCHES OPERATOR? {acct.address.lower() == '0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e'}")
print()

# Save
key_path = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\operator_key.txt"
with open(key_path, "w") as f:
    f.write(NEW_KEY)
print(f"Saved to {key_path}")

# Check balance
def get_usdc(addr):
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://base.blockscout.com/api/v2/addresses/{addr}/token-balances", headers=HEADERS),
                context=ctx, timeout=15) as r:
            items = json.loads(r.read().decode())
            if not isinstance(items, list): items = items.get("items", [])
            for b in items:
                tok = b.get("token", {}) or {}
                if tok.get("symbol", "").upper() == "USDC":
                    val = b.get("value", "0")
                    if val.startswith("0x"):
                        return int(val, 16) / 1e6
                    return int(val) / 1e6
            return 0
    except Exception as e:
        return None

def get_eth(addr):
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://base.blockscout.com/api/v2/addresses/{addr}", headers=HEADERS),
                context=ctx, timeout=15) as r:
            j = json.loads(r.read().decode())
            cb = j.get("coin_balance")
            if cb:
                if cb.startswith("0x"):
                    return int(cb, 16) / 1e18
                return int(cb) / 1e18
            return 0
    except: return None

# Check all known wallets
WALLETS = {
    "OPERATOR (new key)": acct.address,
    "D32A": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
    "OTHER-KEY": "0xb10871882b12051b5531dBcaf0a564082aB41CeF",
}

# Map key to address
KEY_MAP = {
    "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2": "0x3f94d512869900c94cc9f0e2d54b203d966a1697e41b04d5d51d8622f0a9e490",
    acct.address.lower(): NEW_KEY,
    "0xb10871882b12051b5531dBcaf0a564082aB41CeF": "0x758ced3b12c9462340867c7f523476f3f9c4d7af08360185b33d5eb224a06bda",
}

print()
for label, addr in WALLETS.items():
    usdc = get_usdc(addr)
    eth = get_eth(addr)
    print(f"  {label}: {addr}")
    print(f"    USDC: {usdc}")
    print(f"    ETH: {eth}")
    has_key = addr.lower() in KEY_MAP
    print(f"    I have key: {has_key}")
    print()
