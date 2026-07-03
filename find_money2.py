#!/usr/bin/env python3
"""Robust check across all chains."""
import json, urllib.request, ssl, urllib.error

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

addresses = {
    "USER_KEY": "0xb10871882b12051b5531dBcaf0a564082aB41CeF",
    "MY-GEN": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
    "OPERATOR": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
}

# Multiple chains - try the ones Google Cloud faucet could have used
CHAINS_BLOCKSCOUT = [
    ("base-sepolia", "Base Sepolia (84532)"),
    ("base", "Base Mainnet (8453)"),
    ("ethereum-sepolia", "Ethereum Sepolia (11155111)"),
    ("optimism-sepolia", "OP Sepolia (11155420)"),
    ("arbitrum-sepolia", "Arbitrum Sepolia (421614)"),
    ("optimism", "OP Mainnet (10)"),
    ("ethereum", "Ethereum Mainnet (1)"),
]

def blockscout(path, chain):
    url = f"https://{chain}.blockscout.com/api/v2/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as ex:
        return ex.code, {"error": ex.read().decode()[:200]}
    except Exception as e:
        return 0, {"error": str(e)}

# Check each address on each chain
for label, addr in addresses.items():
    print(f"\n{'='*70}")
    print(f"{label}: {addr}")
    print(f"{'='*70}")
    found_any = False
    for chain_id, chain_name in CHAINS_BLOCKSCOUT:
        # Address info
        s, r = blockscout(f"addresses/{addr}", chain_id)
        if s == 200:
            cb = r.get("coin_balance")
            eth = 0
            if cb:
                try:
                    eth = (int(cb, 16) if cb.startswith("0x") else int(cb)) / 1e18
                except: pass
            tx_count = r.get("transactions_count") or 0
            if eth > 0 or tx_count > 0:
                print(f"  [{chain_name}] ETH={eth:.10f}  txs={tx_count}  ***FOUND***")
                found_any = True

        # Token balances
        s, r = blockscout(f"addresses/{addr}/token-balances", chain_id)
        if s == 200:
            items = r if isinstance(r, list) else r.get("items", [])
            for b in items:
                tok = b.get("token", {}) or {}
                sym = tok.get("symbol", "?")
                dec_raw = tok.get("decimals")
                decimals = int(dec_raw) if dec_raw is not None else 18
                val = b.get("value", "0") or "0"
                if val.startswith("0x"):
                    val_int = int(val, 16)
                else:
                    val_int = int(val) if val else 0
                human = val_int / (10 ** decimals)
                if human > 0:
                    print(f"  [{chain_name}] {sym}: {human}  ***FOUND***")
                    found_any = True
    if not found_any:
        print(f"  >> No funds on any chain I can check. NOTHING HERE.")
