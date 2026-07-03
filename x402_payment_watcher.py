#!/usr/bin/env python3
"""Watch the operator wallet for incoming USDC.
Also accepts a private key for the operator wallet so we can do the x402 payment.
When USDC >= 0.01 lands, sign EIP-3009 authorization and call AIA worker.
Then check CDP Bazaar for AIA listing."""
import os, json, time, secrets, urllib.request, ssl, urllib.error, sys, traceback

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

# ============================================================
# CONFIG
# ============================================================
OPERATOR = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
AIA_WORKER = "https://aia-x402.rmalka06.workers.dev"
CDP_BAZAAR = "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources"
PRICE_USDC = "10000"  # 0.01 USDC

# Wallets I can spend from
WALLETS = {
    "GEN-0xD32A": {
        "address": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
        "private_key": "0x3f94d512869900c94cc9f0e2d54b203d966a1697e41b04d5d51d8622f0a9e490"
    }
}

# Read operator key from file if user dropped it
op_key_file = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\operator_key.txt"
if os.path.exists(op_key_file):
    with open(op_key_file) as f:
        k = f.read().strip()
    if k.startswith("0x") and len(k) == 66:
        from eth_account import Account
        addr = Account.from_key(k).address
        if addr.lower() == OPERATOR.lower():
            WALLETS["OPERATOR"] = {"address": addr, "private_key": k}
            print(f"  ✓ loaded operator key from {op_key_file}")

# ============================================================
# CHECK BALANCE
# ============================================================
def get_usdc_balance(addr):
    """Get USDC balance via Blockscout."""
    url = f"https://base.blockscout.com/api/v2/addresses/{addr}/token-balances"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
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

def get_eth_balance(addr):
    url = f"https://base.blockscout.com/api/v2/addresses/{addr}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            j = json.loads(r.read().decode())
            cb = j.get("coin_balance")
            if cb:
                if cb.startswith("0x"):
                    return int(cb, 16) / 1e18
                return int(cb) / 1e18
            return 0
    except Exception as e:
        return None

# ============================================================
# X402 PAYMENT
# ============================================================
def call_aia_with_payment(payer_key, payer_addr, aia_url=AIA_WORKER + "/v1/signals?limit=1"):
    """Call AIA worker with a real x402 payment."""
    from eth_account import Account
    from eth_account.messages import encode_typed_data

    # 1) Get 402 response
    print(f"\n  → Calling {aia_url} (no payment)")
    req = urllib.request.Request(aia_url, headers={**HEADERS, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            # Got 200 — already free?
            body = r.read().decode()
            print(f"  ⚠ Got 200 without payment: {body[:200]}")
            return False, body
    except urllib.error.HTTPError as e:
        if e.code != 402:
            return False, f"HTTP {e.code}: {e.read().decode()[:300]}"
        # 402 — extract PAYMENT-REQUIRED
        pr = e.headers.get("PAYMENT-REQUIRED")
        if not pr:
            return False, "no PAYMENT-REQUIRED header"
        import base64
        pr_json = json.loads(base64.b64decode(pr).decode())
        accept = pr_json["accepts"][0]
        print(f"  → Got 402, price={accept['maxAmountRequired']} ({accept.get('asset', '?')})")

    # 2) Sign EIP-3009 TransferWithAuthorization
    valid_before = int(time.time()) + 300
    nonce_bytes = "0x" + secrets.token_hex(32)

    domain = {
        "name": "USD Coin",
        "version": "2",
        "chainId": 8453,  # Base mainnet
        "verifyingContract": USDC_BASE
    }
    types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"}
        ]
    }
    msg = {
        "from": payer_addr,
        "to": accept["payTo"],
        "value": accept["maxAmountRequired"],
        "validAfter": 0,
        "validBefore": valid_before,
        "nonce": nonce_bytes
    }
    typed = encode_typed_data(domain, types, msg)
    signed = Account.sign_message(typed, payer_key)
    authorization = {
        "from": msg["from"],
        "to": msg["to"],
        "value": msg["value"],
        "validAfter": msg["validAfter"],
        "validBefore": msg["validBefore"],
        "nonce": msg["nonce"],
        "v": int(signed.v),
        "r": hex(signed.r),
        "s": hex(signed.s)
    }

    # 3) Build x402 payment payload
    payload = {
        "x402Version": 2,
        "scheme": accept["scheme"],
        "network": accept["network"],
        "payload": {
            "signature": authorization,
            "authorization": authorization
        }
    }
    sig_b64 = base64.b64encode(json.dumps(payload).encode()).decode()

    # 4) POST with X-PAYMENT header
    print(f"  → Posting with X-PAYMENT (sig {len(sig_b64)}b)")
    req = urllib.request.Request(aia_url, headers={
        **HEADERS,
        "Accept": "application/json",
        "X-PAYMENT": sig_b64,
        "PAYMENT-SIGNATURE": sig_b64
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            body = r.read().decode()
            pr_resp = r.headers.get("PAYMENT-RESPONSE")
            if pr_resp:
                try:
                    prj = json.loads(base64.b64decode(pr_resp).decode())
                    print(f"  → PAYMENT-RESPONSE: {json.dumps(prj)[:500]}")
                except: pass
            print(f"  ✓ HTTP {r.status} ({len(body)}b)")
            print(f"    body: {body[:300]}")
            return True, body
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        pr_resp = e.headers.get("PAYMENT-RESPONSE")
        if pr_resp:
            try:
                prj = json.loads(base64.b64decode(pr_resp).decode())
                print(f"  → PAYMENT-RESPONSE: {json.dumps(prj)[:500]}")
            except: pass
        print(f"  ✗ HTTP {e.code} ({len(body)}b)")
        print(f"    body: {body[:500]}")
        return False, body

# ============================================================
# CHECK CDP BAZAAR FOR AIA
# ============================================================
def check_aia_in_bazaar():
    """Query CDP Bazaar for AIA."""
    # Wait a moment for indexing
    print(f"\n  → Checking CDP Bazaar for AIA (query='aia')...")
    url = f"{CDP_BAZAAR}?q=aia&limit=20"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            j = json.loads(r.read().decode())
            items = j.get("items", [])
            print(f"  → {len(items)} items match 'aia'")
            for it in items:
                if "rmalka" in str(it).lower() or "aia-x402" in str(it).lower():
                    print(f"  ✓ FOUND AIA: {it.get('resource')} | payTo: {it.get('accepts',[{}])[0].get('payTo','?')}")
                    return True, it
            # Maybe under a different search
            for q in ["razel369", "rmalka", "Autonomous Insight", "AI signal"]:
                url = f"{CDP_BAZAAR}?q={q}&limit=20"
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
                    j = json.loads(r.read().decode())
                    items = j.get("items", [])
                    for it in items:
                        if "rmalka" in str(it).lower() or "aia-x402" in str(it).lower():
                            print(f"  ✓ FOUND AIA via q={q}: {it.get('resource')}")
                            return True, it
            print(f"  ✗ AIA not yet in CDP Bazaar (may need 30-60s for indexing)")
            return False, None
    except Exception as e:
        print(f"  ERR: {e}")
        return False, None

# ============================================================
# MAIN LOOP
# ============================================================
print("=" * 70)
print("X402 PAYMENT WATCHER + AUTO-INDEXER")
print("=" * 70)
print(f"Watching: {OPERATOR}")
print(f"Wallets I control: {[w['address'] for w in WALLETS.values()]}")
print()

DONE = False
for i in range(120):  # 10 minutes max
    print(f"--- Check {i+1} at {time.strftime('%H:%M:%S')} ---")
    for label, wallet in WALLETS.items():
        bal = get_usdc_balance(wallet["address"])
        if bal is None:
            print(f"  {label} ({wallet['address'][:10]}...): balance check failed")
            continue
        eth = get_eth_balance(wallet["address"])
        print(f"  {label} ({wallet['address'][:10]}...): USDC=${bal:.4f}  ETH={eth or 0:.8f}")
        if bal >= 0.01 and eth and eth > 0.000005:
            # Need ETH for gas, USDC for payment
            print(f"  ✓ Has USDC + ETH — making x402 payment!")
            ok, result = call_aia_with_payment(wallet["private_key"], wallet["address"])
            if ok:
                # Wait for CDP indexing
                time.sleep(10)
                found, item = check_aia_in_bazaar()
                if found:
                    print("\n  ✓✓✓ AIA IS IN THE CDP BAZAAR — VISIBLE TO ALL X402 BUYERS")
                    DONE = True
                    break
                # Try one more time after 30s
                time.sleep(30)
                found, item = check_aia_in_bazaar()
                if found:
                    print("\n  ✓✓✓ AIA IS IN THE CDP BAZAAR")
                    DONE = True
                    break
            # Payment failed or not yet indexed
            print(f"  Will retry in 15s...")
    if DONE:
        break
    time.sleep(15)

print()
print("=" * 70)
print("DONE")
print("=" * 70)
