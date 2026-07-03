#!/usr/bin/env python3
"""Quick wallet check via Blockscout — no wrangler."""
import json, urllib.request, ssl, urllib.error

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

# 1) Address info
print("=" * 60)
print(f"BLOCKSCOUT ADDRESS: {WALLET}")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}"
status, body = fetch(url)
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    cb = j.get("coin_balance")
    if cb:
        # blockscout returns wei as string with no 0x prefix sometimes
        try:
            cb_int = int(cb, 16) if cb.startswith("0x") else int(cb)
            print(f"  ETH balance: {cb_int / 1e18:.10f} ({cb_int} wei)")
        except:
            print(f"  ETH balance raw: {cb}")
    print(f"  tx_count: {j.get('transactions_count')}")
    print(f"  is_contract: {j.get('is_contract')}")
    print(f"  creator: {j.get('creator_address_hash')}")
print()

# 2) Token transfers (with token filter to USDC)
print("=" * 60)
print("USDC TOKEN TRANSFERS")
print("=" * 60)
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/token-transfers?token={USDC}"
status, body = fetch(url)
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    items = j.get("items", [])
    print(f"  total USDC transfers: {len(items)}")
    if not items:
        print(f"  --> zero USDC activity on this wallet")
    for t in items[:5]:
        v = t.get("total", {})
        val = v.get("value", "?")
        frm = t.get("from", {}).get("hash", "?")
        to = t.get("to", {}).get("hash", "?")
        direction = "IN " if to.lower() == WALLET.lower() else "OUT"
        print(f"    {direction}: {val}, {frm[:14]}... -> {to[:14]}..., block {t.get('block_number')}")
print()

# 3) All token transfers
print("=" * 60)
print("ALL TOKEN TRANSFERS")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/token-transfers"
status, body = fetch(url)
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    items = j.get("items", [])
    print(f"  total token transfers: {len(items)}")
    if not items:
        print(f"  --> wallet has never received or sent any ERC-20 token")
    for t in items[:10]:
        v = t.get("total", {})
        tok = t.get("token", {})
        sym = tok.get("symbol", "?")
        val = v.get("value", "?")
        frm = t.get("from", {}).get("hash", "?")
        to = t.get("to", {}).get("hash", "?")
        direction = "IN " if to.lower() == WALLET.lower() else "OUT"
        print(f"    {direction}: {val} {sym}, {frm[:14]}... -> {to[:14]}..., block {t.get('block_number')}")
print()

# 4) Transactions
print("=" * 60)
print("BLOCKSCOUT TRANSACTIONS")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/transactions"
status, body = fetch(url)
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    items = j.get("items", [])
    print(f"  total transactions: {len(items)}")
    if not items:
        print(f"  --> wallet has never sent or received any native ETH on Base")
    for t in items[:5]:
        v = t.get("value", "0")
        try:
            v_int = int(v, 16) if v.startswith("0x") else int(v)
        except:
            v_int = 0
        val = v_int / 1e18
        frm = t.get("from", {}).get("hash", "?")
        to_h = t.get("to", {}).get("hash", "?") if t.get("to") else "0x0"
        is_in = to_h.lower() == WALLET.lower()
        is_out = frm.lower() == WALLET.lower()
        direction = "IN " if is_in else ("OUT" if is_out else "OTHER")
        print(f"    {direction}: {val:.10f} ETH, {frm[:14]}... -> {to_h[:14]}..., block {t.get('block')}, hash {t.get('hash','')[:20]}, method {t.get('method','?')}")
print()

# 5) Internal transactions
print("=" * 60)
print("INTERNAL TRANSACTIONS")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/internal-transactions"
status, body = fetch(url)
print(f"  status: {status}")
print(f"  body[:300]: {body[:300]}")
print()

# 6) Verify search for this address on Base
print("=" * 60)
print("ADDRESS SEARCH")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/search?q={WALLET}"
status, body = fetch(url)
print(f"  status: {status}")
if status == 200:
    j = json.loads(body)
    print(f"  body[:500]: {body[:500]}")
