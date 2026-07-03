#!/usr/bin/env python3
"""Check both mainnet AND testnet for this wallet — user may have sent to wrong network."""
import json, urllib.request, ssl, urllib.error

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

addr = "0xb10871882b12051b5531dBcaf0a564082aB41CeF"

# Use Blockscout (works for any chain via URL)
def blockscout(addr, chain="base"):
    url = f"https://{chain}.blockscout.com/api/v2/addresses/{addr}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:300]}
    except Exception as e:
        return 0, {"error": str(e)}

print(f"Wallet: {addr}")
print()

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
        print(f"  tx count: {r.get('transactions_count')}")
        print(f"  is_contract: {r.get('is_contract')}")
        print(f"  creator: {r.get('creator_address_hash')}")
    else:
        print(f"  ERR: {s} {r}")

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
