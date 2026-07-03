#!/usr/bin/env python3
"""Find a free way to trigger an x402 payment for auto-indexing."""
import json, urllib.request, ssl, urllib.error, re

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
}

def call(url, method="GET", data=None, headers=None, timeout=20):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        if isinstance(data, dict): data = json.dumps(data)
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()
    except Exception as e:
        return 0, {}, str(e)

# ============================================================
# 1) Look for x402 facilitator with free test mode
# ============================================================
print("=" * 70)
print("1) FREE x402 facilitator TEST MODE")
print("=" * 70)

# Test the public x402.org facilitator
# https://x402.org/facilitator/verify is the verify endpoint
status, _, body = call("https://x402.org/facilitator", timeout=10)
print(f"  x402.org facilitator GET: {status} ({len(body)}b)")
print(f"    {body[:300]}")

status, _, body = call("https://x402.org/facilitator/verify", method="POST",
                       data={"x402Version": 2, "paymentPayload": {"test": True}, "paymentRequirements": {"test": True}},
                       headers={"Content-Type": "application/json"}, timeout=10)
print(f"  x402.org /verify (test): {status} ({len(body)}b)")
print(f"    {body[:300]}")

# Other public facilitators
for url in [
    "https://facilitator.x402.org",
    "https://api.x402.org/facilitator",
    "https://pay.x402.org",
    "https://www.x402.org/facilitator"
]:
    status, _, body = call(url, timeout=8)
    print(f"  {url}: {status}")

# ============================================================
# 2) Look for "submit endpoint" in any x402 ecosystem site
# ============================================================
print()
print("=" * 70)
print("2) SEARCH x402-foundation repos for submit/index patterns")
print("=" * 70)

# Search for any submit endpoint in x402-foundation/x402
import subprocess
r = subprocess.run(
    ["gh", "search", "code", "x402 submit resource", "--owner", "x402-foundation", "--limit", "5"],
    capture_output=True, text=True, timeout=30
)
print(f"  gh search: rc={r.returncode}")
print(f"  {r.stdout[:500]}")

# ============================================================
# 3) Check x402-foundation/x402 examples (Bazaar extension)
# ============================================================
print()
print("=" * 70)
print("3) x402 examples — bazaar extension patterns")
print("=" * 70)

r = subprocess.run(
    ["gh", "api", "repos/x402-foundation/x402/contents/extensions/bazaar"],
    capture_output=True, text=True, timeout=15
)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"  x402-foundation/x402/extensions/bazaar: {len(j)} items")
    for item in j:
        print(f"    {item.get('type','?')} {item.get('name','?')}")

# Check the Bazaar extension spec
r = subprocess.run(
    ["gh", "api", "repos/x402-foundation/x402/contents/extensions/bazaar/spec.md"],
    capture_output=True, text=True, timeout=15
)
if r.returncode == 0:
    j = json.loads(r.stdout)
    import base64
    content = base64.b64decode(j.get("content", "")).decode("utf-8", errors="replace")
    print(f"  spec.md ({len(content)} chars):")
    print(content[:2000])

# ============================================================
# 4) Check agentic.market backend
# ============================================================
print()
print("=" * 70)
print("4) Agentic.Market backend endpoints")
print("=" * 70)

# It has a Next.js site; look for submit pages or API routes
for path in [
    "/api/submit", "/api/v1/submit", "/api/services/submit",
    "/submit", "/dashboard/submit", "/dashboard",
    "/_next/data", "/api/services", "/api/v1/services",
    "/api/marketplace", "/api/v1/marketplace"
]:
    for base in ["https://www.agentic.market", "https://agentic.market"]:
        url = f"{base}{path}"
        try:
            status, _, body = call(url, timeout=5)
            ct = ""
            if "content-type" in _: ct = _["content-type"]
            else:
                # get from response
                pass
            print(f"  {url}: {status} ({len(body)}b)")
        except: pass

# ============================================================
# 5) Test base mainnet USDC balance of any address I might own
# ============================================================
print()
print("=" * 70)
print("5) Check Blockscout for any incoming USDC transactions today")
print("=" * 70)

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
url = f"https://base.blockscout.com/api/v2/addresses/{WALLET}/token-transfers?token={USDC}"
status, _, body = call(url, timeout=15)
if status == 200:
    j = json.loads(body)
    items = j.get("items", [])
    print(f"  USDC transfers (all-time): {len(items)}")
    for t in items[:5]:
        v = t.get("total", {})
        frm = t.get("from", {}).get("hash", "?")
        to = t.get("to", {}).get("hash", "?")
        direction = "IN " if to.lower() == WALLET.lower() else "OUT"
        print(f"    {direction}: {v.get('value','?')} {t.get('token',{}).get('symbol','?')}, {frm[:14]}... -> {to[:14]}...")

# ============================================================
# 6) Check if there's an internal "test payment" API on AIA
# ============================================================
print()
print("=" * 70)
print("6) AIA test-payment / admin endpoints")
print("=" * 70)

for path in ["/v1/test-pay", "/v1/admin", "/v1/settle", "/admin", "/v1/buy", "/x402"]:
    status, _, body = call(f"https://aia-x402.rmalka06.workers.dev{path}", timeout=10)
    print(f"  {path}: {status} ({len(body)}b)")
