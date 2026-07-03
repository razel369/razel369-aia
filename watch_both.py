#!/usr/bin/env python3
"""Watch BOTH D32A and 0x86f36 wallets. When either has USDC + ETH, fire x402 payment."""
import os, json, time, secrets, urllib.request, ssl, urllib.error, base64, sys

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

# Two wallets I can spend from
WALLETS = {
    "D32A": {
        "address": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
        "private_key": "0x3f94d512869900c94cc9f0e2d54b203d966a1697e41b04d5d51d8622f0a9e490"
    },
    "0x86f36": {
        "address": "0x86f3666720d54c531c723201BA49403D7c42c564",
        "private_key": "0xb833d9773642fa746fa22484eac8f82fa4dca6e87532d0bce23cfc3be094b06d"
    }
}

USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
AIA = "https://aia-x402.rmalka06.workers.dev"

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

def make_payment(wallet, path="/v1/signals?limit=1"):
    from eth_account import Account
    from eth_account.messages import encode_typed_data
    addr = wallet["address"]
    key = wallet["private_key"]
    url = AIA + path
    print(f"\n  → {url}")
    req = urllib.request.Request(url, headers={**HEADERS, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            print(f"  ⚠ Got 200: {r.read().decode()[:200]}")
            return True
    except urllib.error.HTTPError as e:
        if e.code != 402:
            print(f"  ERR HTTP {e.code}: {e.read().decode()[:300]}")
            return False
        pr = e.headers.get("PAYMENT-REQUIRED")
        if not pr: return False
        pr_json = json.loads(base64.b64decode(pr).decode())
        accept = pr_json["accepts"][0]
        print(f"  → Got 402, price={accept['maxAmountRequired']}")

    valid_before = int(time.time()) + 300
    nonce = "0x" + secrets.token_hex(32)
    domain = {"name": "USD Coin", "version": "2", "chainId": 8453, "verifyingContract": USDC_BASE}
    types = {"TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"}
    ]}
    msg = {"from": addr, "to": accept["payTo"], "value": accept["maxAmountRequired"],
           "validAfter": 0, "validBefore": valid_before, "nonce": nonce}
    typed = encode_typed_data(domain, types, msg)
    signed = Account.sign_message(typed, key)
    auth = {"from": msg["from"], "to": msg["to"], "value": msg["value"],
            "validAfter": 0, "validBefore": valid_before, "nonce": nonce,
            "v": int(signed.v), "r": hex(signed.r), "s": hex(signed.s)}
    payload = {"x402Version": 2, "scheme": accept["scheme"], "network": accept["network"],
               "payload": {"signature": auth, "authorization": auth}}
    sig_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    req = urllib.request.Request(url, headers={
        **HEADERS, "Accept": "application/json",
        "X-PAYMENT": sig_b64, "PAYMENT-SIGNATURE": sig_b64
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            body = r.read().decode()
            pr = r.headers.get("PAYMENT-RESPONSE")
            if pr:
                try: print(f"  PAY-RESP: {json.loads(base64.b64decode(pr).decode())}")
                except: pass
            print(f"  ✓ HTTP {r.status} ({len(body)}b)")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        pr = e.headers.get("PAYMENT-RESPONSE")
        if pr:
            try: print(f"  PAY-RESP: {json.loads(base64.b64decode(pr).decode())}")
            except: pass
        print(f"  ✗ HTTP {e.code}: {body[:500]}")
        return False

def check_bazaar():
    for q in ["aia", "razel369", "rmalka", "Autonomous Insight", "aia-x402", "signal", "x402-ai-signal"]:
        url = f"https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?q={q}&limit=20"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), context=ctx, timeout=15) as r:
                items = json.loads(r.read().decode()).get("items", [])
                for it in items:
                    s = json.dumps(it)
                    if "rmalka" in s.lower() or "aia-x402" in s or "razel369" in s.lower():
                        print(f"  ✓ FOUND in CDP Bazaar via q={q}: {it.get('resource')}")
                        return it
        except: pass
    return None

print("=" * 60)
print("WATCHING 2 WALLETS WITH KEYS")
print("=" * 60)
for label, w in WALLETS.items():
    print(f"  {label}: {w['address']}")
print()

DONE = False
for i in range(180):  # 30 minutes
    print(f"\n[{i+1:3d} {time.strftime('%H:%M:%S')}]")
    for label, w in WALLETS.items():
        usdc = get_usdc(w["address"])
        eth = get_eth(w["address"])
        usdc_str = f"${usdc:.4f}" if usdc is not None else "?"
        eth_str = f"{eth:.10f}" if eth is not None else "?"
        print(f"  {label} ({w['address'][:10]}...): USDC={usdc_str}  ETH={eth_str}", end="")
        sys.stdout.flush()
        if usdc is not None and usdc >= 0.005:
            print(f"  ✓ USDC ARRIVED")
            if eth and eth > 0.000005:
                result = make_payment(w, "/v1/signals?limit=1")
                if result:
                    print("\n  → Waiting 15s for CDP indexing...")
                    time.sleep(15)
                    item = check_bazaar()
                    if not item:
                        print("  → Not in Bazaar yet, waiting 30s...")
                        time.sleep(30)
                        item = check_bazaar()
                    if item:
                        print(f"\n  ✓✓✓ AIA LIVE IN CDP BAZAAR")
                    else:
                        print(f"\n  Payment worked, indexing may take more time")
                    DONE = True
                    break
                else:
                    print("  → Payment failed, will keep watching")
            else:
                print(f"  → Need ETH for gas, will wait")
        else:
            print()
    if DONE:
        break
    time.sleep(10)
