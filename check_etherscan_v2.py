#!/usr/bin/env python3
"""Use Etherscan V2 API to check Base balance."""
import json, urllib.request, ssl, urllib.error

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# Etherscan V2 unified API: chainid=8453 is Base
print("Wallet:", WALLET)
print()

# Native ETH
url = f"https://api.etherscan.io/v2/api?chainid=8453&module=account&action=balance&address={WALLET}&tag=latest"
status, body = fetch(url)
print(f"ETH: status={status}")
print(f"  {body[:300]}")
if '"status":"1"' in body:
    j = json.loads(body)
    bal_wei = int(j["result"])
    print(f"  balance: {bal_wei / 1e18:.10f} ETH")
print()

# USDC token
url = f"https://api.etherscan.io/v2/api?chainid=8453&module=account&action=tokenbalance&contractaddress={USDC}&address={WALLET}&tag=latest"
status, body = fetch(url)
print(f"USDC: status={status}")
print(f"  {body[:300]}")
if '"status":"1"' in body:
    j = json.loads(body)
    bal_raw = int(j["result"])
    print(f"  balance: ${bal_raw / 1_000_000:.6f} USDC")
print()

# Recent transactions (incoming only)
url = f"https://api.etherscan.io/v2/api?chainid=8453&module=account&action=txlist&address={WALLET}&startblock=0&endblock=99999999&page=1&offset=20&sort=desc"
status, body = fetch(url)
print(f"TX list: status={status}")
print(f"  {body[:500]}")
if '"status":"1"' in body:
    j = json.loads(body)
    txs = j.get("result", [])
    print(f"  total txs: {len(txs)}")
    incoming = [t for t in txs if t.get("to", "").lower() == WALLET.lower()]
    outgoing = [t for t in txs if t.get("from", "").lower() == WALLET.lower()]
    print(f"  incoming: {len(incoming)}, outgoing: {len(outgoing)}")
    for t in incoming[:5]:
        val = int(t["value"]) / 1e18
        frm = t.get("from", "?")
        print(f"    IN: {val} ETH from {frm} (block {t.get('blockNumber')}, {t.get('timeStamp','')})")
    for t in outgoing[:5]:
        val = int(t["value"]) / 1e18
        to = t.get("to", "?")
        print(f"    OUT: {val} ETH to {to} (block {t.get('blockNumber')})")
print()

# Token transfer events (USDC ERC20)
url = f"https://api.etherscan.io/v2/api?chainid=8453&module=account&action=tokentx&contractaddress={USDC}&address={WALLET}&page=1&offset=20&sort=desc"
status, body = fetch(url)
print(f"USDC token transfers: status={status}")
print(f"  {body[:500]}")
if '"status":"1"' in body:
    j = json.loads(body)
    txs = j.get("result", [])
    print(f"  total token txs: {len(txs)}")
    for t in txs[:5]:
        val = int(t["value"]) / 1_000_000
        frm = t.get("from", "?")
        to = t.get("to", "?")
        direction = "IN " if to.lower() == WALLET.lower() else "OUT"
        print(f"    {direction}: ${val} USDC, {frm[:14]}... -> {to[:14]}..., block {t.get('blockNumber')}, hash {t.get('hash','')[:20]}")
