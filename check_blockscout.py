#!/usr/bin/env python3
"""Check Base wallet balance via Blockscout (no Cloudflare bot block)."""
import json, urllib.request, ssl, urllib.error

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

ctx = ssl.create_default_context()

# Headers mimicking a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch(url, method="GET", data=None, headers=None):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST", headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

print(f"Wallet: {WALLET}\n")

# 1) Blockscout v2 (Base has it at base.blockscout.com)
endpoints = [
    f"https://base.blockscout.com/api/v2/addresses/{WALLET}",
    f"https://base.blockscout.com/api/v2/addresses/{WALLET}/token-balances",
    f"https://base.blockscout.com/api/v2/addresses/{WALLET}/transactions?filter=to%20%7C%20from",
]

for url in endpoints:
    print(f"--- {url[:90]}{'...' if len(url) > 90 else ''}")
    status, body = fetch(url)
    print(f"  status: {status}")
    if status == 200:
        try:
            j = json.loads(body)
            if "token_balances" in url:
                bals = j if isinstance(j, list) else j.get("items", [])
                if not bals:
                    print(f"  no token balances")
                for b in bals[:10]:
                    tok = b.get("token", {})
                    sym = tok.get("symbol", "?")
                    name = tok.get("name", "?")
                    decimals = int(tok.get("decimals", 18))
                    val = b.get("value", "0")
                    if val and val.startswith("0x"):
                        val_int = int(val, 16)
                    else:
                        val_int = int(val) if val else 0
                    human = val_int / (10 ** decimals)
                    print(f"    {sym} ({name}): {human}")
            elif "addresses" in url and "token-balances" not in url:
                print(f"  ETH balance: {j.get('coin_balance', '?')}")
                print(f"  tx count: {j.get('transactions_count', '?')}")
            elif "transactions" in url:
                txs = j.get("items", [])
                print(f"  total txs: {j.get('total_count', '?')}, fetched: {len(txs)}")
                for t in txs[:5]:
                    val = int(t.get("value", "0")) / 1e18
                    method = t.get("method", "")
                    frm = t.get("from", {}).get("hash", "?")[:14]
                    to = t.get("to", {}).get("hash", "?") if t.get("to") else "0x0"
                    print(f"    {t.get('timestamp','')} {frm}... -> {to[:14]}... {val} ETH [{method}]")
        except json.JSONDecodeError:
            print(f"  body: {body[:300]}")
    else:
        print(f"  body: {body[:300]}")
    print()

# 2) Basescan API (no key, limited)
print("--- Basescan API (no key) ---")
url = f"https://api.basescan.org/api?module=account&action=balance&address={WALLET}&tag=latest"
status, body = fetch(url)
print(f"  ETH: {status} {body[:200]}")

url = f"https://api.basescan.org/api?module=account&action=tokenbalance&contractaddress={USDC}&address={WALLET}&tag=latest"
status, body = fetch(url)
print(f"  USDC: {status} {body[:200]}")
