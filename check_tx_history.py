#!/usr/bin/env python3
"""Check D32A and other wallets' FULL transaction history (not just balance).
Also try to find ANY activity."""
import os, json, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

def call(url, method="GET", data=None, timeout=15):
    h = dict(HEADERS)
    if data is not None:
        if isinstance(data, dict): data = json.dumps(data)
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

wallets = {
    "OPERATOR": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "D32A": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
    "0x86f36": "0x86f3666720d54c531c723201BA49403D7c42c564",
    "0xb108": "0xb10871882b12051b5531dBcaf0a564082aB41CeF",
}

# Check transaction history on multiple chains
for label, addr in wallets.items():
    print(f"\n{'='*60}")
    print(f"{label}: {addr}")
    print(f"{'='*60}")
    found_any = False
    for chain in ["base", "base-sepolia", "ethereum", "ethereum-sepolia", "optimism", "optimism-sepolia", "arbitrum"]:
        s, b = call(f"https://{chain}.blockscout.com/api/v2/addresses/{addr}/transactions")
        if s == 200:
            try:
                j = json.loads(b)
                items = j.get("items", [])
                if items:
                    found_any = True
                    print(f"  [{chain}] {len(items)} txs")
                    for t in items[:3]:
                        v = int(t.get("value", "0") or "0") / 1e18
                        frm = t.get("from", {}).get("hash", "?")
                        to_h = (t.get("to", {}) or {}).get("hash", "0x0")
                        direction = "IN " if to_h.lower() == addr.lower() else "OUT"
                        block = t.get("block")
                        method = t.get("method", "")
                        ts = t.get("timestamp", "")
                        print(f"    {direction}: {v:.10f} ETH ({method}) {frm[:10]}..→{to_h[:10]}.. block {block} {ts}")
            except: pass

    if not found_any:
        print(f"  >> NO transactions on any chain I can check")
