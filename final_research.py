#!/usr/bin/env python3
"""Final research: explore OKX AI marketplace URL + look for more platforms + earn concrete money today."""
import os, re, json, urllib.request, ssl, subprocess
from urllib.parse import quote

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

def jina_read(url):
    """Read URL via r.jina.ai"""
    url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:500]}"
    except Exception as e:
        return f"ERR: {e}"

def call(url, method="GET", data=None, headers=None, timeout=20):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

# ============================================================
# 1) Read OKX AI marketplace via Jina
# ============================================================
print("=" * 70)
print("1) OKX AI — find public marketplace URL via Jina reader")
print("=" * 70)

# Try known URLs
for url in [
    "https://www.okx.com/ai",
    "https://www.okx.com/ai/marketplace",
    "https://ai.okx.com",
    "https://onchainos.okx.com",
    "https://onchainos.okx.com/marketplace",
    "https://web3.okx.com",
    "https://www.okx.com/web3/ai"
]:
    print(f"\n--- {url} ---")
    text = jina_read(url)
    if len(text) > 200:
        print(text[:1500])
    else:
        print(f"  short response: {text[:200]}")

# ============================================================
# 2) Try onchainos CLI — actual install
# ============================================================
print()
print("=" * 70)
print("2) ONCHAINOS CLI — install")
print("=" * 70)

# Check if it's already installed
r = subprocess.run(["onchainos","--version"], capture_output=True, text=True, timeout=10, shell=True)
print(f"  onchainos --version: rc={r.returncode}, out={r.stdout[:200]!r}, err={r.stderr[:200]!r}")

# Look in install scripts
r = subprocess.run(["gh","api","repos/okx/onchainos-skills/contents/install.sh"],
                   capture_output=True, text=True, timeout=20)
if r.returncode == 0:
    j = json.loads(r.stdout)
    import base64
    content = base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
    print(f"\n  install.sh ({len(content)} chars):")
    print(content[:1500])

# Try installing via npm
r = subprocess.run(
    "npm install -g @okxweb3/onchainos 2>&1",
    capture_output=True, text=True, timeout=120, shell=True
)
print(f"\n  npm install: rc={r.returncode}")
print(f"  out: {r.stdout[:500]}")
if r.stderr: print(f"  err: {r.stderr[:500]}")

# Check if installed
r = subprocess.run(["onchainos","--help"], capture_output=True, text=True, timeout=10, shell=True)
print(f"\n  onchainos --help: rc={r.returncode}")
if r.stdout: print(f"  out: {r.stdout[:1500]}")
if r.stderr: print(f"  err: {r.stderr[:500]}")

# ============================================================
# 3) Look at all 3 PayanAgent offers on public discover
# ============================================================
print()
print("=" * 70)
print("3) PAYANAGENT — verify my offers are listed")
print("=" * 70)

status, body = call("https://payanagent.com/api/v1/discover?q=aia&limit=10")
print(f"  discover q=aia: {status}")
if status == 200:
    j = json.loads(body)
    offers = j.get("offers", [])
    for o in offers:
        seller = o.get("seller", {})
        print(f"    - {o.get('title','?')[:50]} ${o.get('priceUsd','?')} by {seller.get('name','?')}")

status, body = call("https://payanagent.com/api/v1/discover?q=owockibot&limit=10")
print(f"\n  discover q=owockibot: {status}")
if status == 200:
    j = json.loads(body)
    offers = j.get("offers", [])
    for o in offers:
        seller = o.get("seller", {})
        print(f"    - {o.get('title','?')[:50]} ${o.get('priceUsd','?')} by {seller.get('name','?')}")

# ============================================================
# 4) Try a different Clawlancer bounty with different timing
# ============================================================
print()
print("=" * 70)
print("4) CLAWLANCER — try one more bounty to confirm escrow broken")
print("=" * 70)

# Get a bounty with a VETERAN poster
status, body = call("https://clawlancer.ai/api/listings?listing_type=BOUNTY&status=active&limit=20")
if status == 200:
    j = json.loads(body)
    listings = j.get("listings", [])
    # Find highest priced one
    listings.sort(key=lambda x: x.get("price_wei", 0), reverse=True)
    for l in listings[:3]:
        bid = l.get("id")
        title = l.get("title","?")
        price = l.get("price_wei", 0) / 1_000_000
        if bid:
            CW_PATH = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\clawlancer.json"
            with open(CW_PATH) as f:
                cw = json.load(f)
            API_KEY = cw["api_key"]
            status2, body2 = call(f"https://clawlancer.ai/api/listings/{bid}/claim",
                                  method="POST",
                                  headers={"Authorization": f"Bearer {API_KEY}"})
            print(f"  claim ${price} {title[:50]}: {status2}")
            print(f"    {body2[:400]}")

# ============================================================
# 5) Look for Clawlancer platform's relayer wallet — is it funded?
# ============================================================
print()
print("=" * 70)
print("5) CLAWLANCER RELAYER WALLET check")
print("=" * 70)

# The error showed from: 0x4602973Aa67b70BfD08D299f2AafC084179A8101
# The USDC contract: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
# Check USDC balance of relayer
import urllib.request
RELAYER = "0x4602973Aa67b70BfD08D299f2AafC084179A8101"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Use Blockscout
url = f"https://base.blockscout.com/api/v2/addresses/{RELAYER}"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
    j = json.loads(r.read().decode())
    cb = j.get("coin_balance")
    if cb:
        try:
            cb_int = int(cb, 16) if cb.startswith("0x") else int(cb)
            print(f"  relayer ETH: {cb_int / 1e18:.8f}")
        except: print(f"  relayer ETH: {cb}")
    print(f"  relayer tx_count: {j.get('transactions_count')}")

# USDC balance
url = f"https://base.blockscout.com/api/v2/addresses/{RELAYER}/token-balances"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
    j = json.loads(r.read().decode())
    bals = j if isinstance(j, list) else j.get("items", [])
    print(f"  relayer token balances: {len(bals)}")
    for b in bals[:5]:
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
