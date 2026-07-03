#!/usr/bin/env python3
"""Check Base balance via multiple free endpoints + wrangler properly."""
import json, urllib.request, ssl, urllib.error, subprocess, os

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# 1) Blockscout full address info
print("=" * 60)
print("BLOCKSCOUT FULL ADDRESS INFO")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}"
status, body = fetch(url)
print(f"status: {status}")
if status == 200:
    j = json.loads(body)
    print(f"  hash: {j.get('hash')}")
    print(f"  coin_balance: {j.get('coin_balance')}")
    print(f"  tx_count: {j.get('transactions_count')}")
    print(f"  creation_tx: {j.get('creation_tx_hash')}")
    print(f"  creator: {j.get('creator_address_hash')}")
    print(f"  has_ens: {j.get('has_ens')}")
    print(f"  is_contract: {j.get('is_contract')}")

# 2) Token transfers list
print()
print("=" * 60)
print("BLOCKSCOUT TOKEN TRANSFERS (USDC)")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/token-transfers?filter=to%20%7C%20from&token={USDC}"
status, body = fetch(url)
print(f"status: {status}")
print(f"  body[:800]: {body[:800]}")

# 3) Token transfers (all tokens, no filter)
print()
print("=" * 60)
print("BLOCKSCOUT ALL TOKEN TRANSFERS")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/token-transfers?filter=to%20%7C%20from"
status, body = fetch(url)
print(f"status: {status}")
print(f"  body[:1500]: {body[:1500]}")

# 4) Transactions (no filter syntax)
print()
print("=" * 60)
print("BLOCKSCOUT TRANSACTIONS")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/transactions"
status, body = fetch(url)
print(f"status: {status}")
if status == 200:
    j = json.loads(body)
    items = j.get("items", [])
    print(f"  total: {len(items)}")
    for t in items[:5]:
        val = int(t.get("value", "0")) / 1e18
        frm_h = t.get("from", {}).get("hash", "?")
        to_h = t.get("to", {}).get("hash", "?") if t.get("to") else "0x0"
        is_in = to_h.lower() == WALLET.lower()
        is_out = frm_h.lower() == WALLET.lower()
        direction = "IN" if is_in else ("OUT" if is_out else "OTHER")
        print(f"    {direction}: {val:.8f} ETH, {frm_h[:14]}... -> {to_h[:14]}..., block {t.get('block')}, hash {t.get('hash','')[:20]}, method {t.get('method','?')}")
else:
    print(f"  body[:300]: {body[:300]}")

# 5) Internal transactions
print()
print("=" * 60)
print("BLOCKSCOUT INTERNAL TXS")
print("=" * 60)
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/internal-transactions"
status, body = fetch(url)
print(f"status: {status}")
print(f"  body[:500]: {body[:500]}")

# 6) Cloudflare analytics — wrangler deploys + analytics
print()
print("=" * 60)
print("CLOUDFLARE WRANGLER (cd to worker dir)")
print("=" * 60)
os.chdir(r"C:\Users\rmalk\projects\razel369-aia\cloudflare-worker")
# Check what files are there
for f in os.listdir("."):
    print(f"  {f}")

# wrangler tail — get live logs (start in background, read for 5s)
r = subprocess.run(
    "wrangler tail aia-x402 2>&1",
    capture_output=True, text=True, timeout=8, shell=True
)
print()
print("--- wrangler tail (8s window) ---")
if r.stdout:
    # split by log entries
    lines = r.stdout.strip().split('\n')
    print(f"  {len(lines)} log lines:")
    for line in lines[:30]:
        print(f"    {line[:200]}")
else:
    print(f"  no output")
if r.stderr:
    print(f"  stderr: {r.stderr[:500]}")
