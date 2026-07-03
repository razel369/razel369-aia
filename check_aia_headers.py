#!/usr/bin/env python3
"""Check AIA 402 HEADERS (the bazaar extension is in header, not body!) + find x402scan form action."""
import json, urllib.request, urllib.error, re, base64, time

def fetch_full(url, headers=None, method="GET", data=None, timeout=20):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            return r.status, dict(r.headers), text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        return e.code, dict(e.headers), text
    except Exception as e:
        return -1, {}, str(e)

# 1) AIA 402 - check headers
print("=" * 60)
print("AIA 402 HEADERS (PAYMENT-REQUIRED)")
print("=" * 60)
s, h, b = fetch_full("https://aia-x402.rmalka06.workers.dev/v1/signals",
                     headers={"Accept":"application/json","User-Agent":"Mozilla/5.0"})
print(f"  status: {s}")
print(f"  body: {b[:200]!r}")
print()
pr = h.get("payment-required") or h.get("PAYMENT-REQUIRED") or h.get("X-Payment-Required")
if pr:
    print(f"  PAYMENT-REQUIRED: {pr[:100]}")
    try:
        decoded = json.loads(base64.b64decode(pr))
        print(f"  x402Version: {decoded.get('x402Version')}")
        a0 = decoded.get("accepts",[{}])[0]
        print(f"  accepts[0] outputSchema: {bool(a0.get('outputSchema'))}")
        ext = decoded.get("extensions",{})
        bz = ext.get("bazaar",{})
        svcs = bz.get("services",[])
        print(f"  bazaar.services count: {len(svcs)}")
        for s2 in svcs:
            print(f"    - {s2.get('type')}: {s2.get('resource','')[:80]}")
            print(f"      desc: {s2.get('description','')[:80]}")
            print(f"      tags: {s2.get('tags',[])}")
    except Exception as e:
        print(f"  decode err: {e}")
else:
    print("  NO PAYMENT-REQUIRED HEADER")

# 2) Look at the x402scan register page - find the form action
print()
print("=" * 60)
print("x402scan /resources/register - find form action")
print("=" * 60)
s, h, b = fetch_full("https://x402scan.com/resources/register",
                     headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"})
print(f"  status: {s}, size: {len(b)}")
# Look for fetch calls
print("  References to /api/ or /resources/ in JS data:")
for m in re.finditer(r'\\"(https?://[^"\\]+|/[a-z][a-zA-Z0-9_/-]+(?:/[^"\\]+)?)\\"', b):
    u = m.group(1)
    if any(kw in u.lower() for kw in ['/api','register','submit','service','resource']):
        if len(u) < 200 and 'https://x402' in u or u.startswith('/'):
            print(f"    {u[:120]}")

# 3) Try a direct API call to /api/resources/register
print()
print("=" * 60)
print("x402scan POST /api/resources/register")
print("=" * 60)
service = {
    "name": "AIA Real-Time Signal Stream",
    "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
    "description": "Filtered curated AI/agent/crypto/finance signals from HN, GitHub, V2EX, dev.to, Lobsters",
    "tags": ["ai","agents","signals","curation","research","x402"],
    "price": "0.01",
    "currency": "USDC",
    "network": "base",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "payTo": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "operator": "@razel369"
}
for path in [
    "/api/resources/register",
    "/api/resources",
    "/api/services/register",
    "/api/v1/resources",
    "/api/public/resources/register",
    "/api/public/resources",
]:
    s, h, b = fetch_full(f"https://x402scan.com{path}", method="POST", data=service,
                         headers={"Accept":"application/json","User-Agent":"Mozilla/5.0"})
    print(f"  {s} {path}")
    if isinstance(b, str) and len(b) < 500:
        print(f"    {b[:200]}")

# 4) Look at x402scan.com /resources page (parent of register)
print()
print("=" * 60)
print("x402scan /resources")
print("=" * 60)
s, h, b = fetch_full("https://x402scan.com/resources",
                     headers={"User-Agent":"Mozilla/5.0"})
print(f"  status: {s}, size: {len(b)}")
for m in re.finditer(r'href="(/resources/[^"]+)"', b):
    print(f"  {m.group(1)}")
