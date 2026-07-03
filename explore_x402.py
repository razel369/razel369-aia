#!/usr/bin/env python3
"""Look at AIA 402 raw + try other x402 discovery + check the actual services on agentic.market."""
import json, urllib.request, urllib.error, base64, time

def fetch(url, headers=None, method="GET", data=None, timeout=20):
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
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e:
        return -1, str(e)

# 1) AIA 402 - get raw text
print("=" * 60)
print("AIA 402 RAW TEXT")
print("=" * 60)
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/signals",
             headers={"Accept":"application/json","User-Agent":"curl/7.88.1"})
print(f"  status: {s}")
if isinstance(d, str):
    # Try to parse and pretty print
    try:
        j = json.loads(d)
        pr_b64 = j.get("paymentRequired") or j.get("payment_required")
        if pr_b64:
            decoded = json.loads(base64.b64decode(pr_b64))
            print(f"  x402v={decoded.get('x402Version')}")
            print(f"  accepts[0]: {json.dumps(decoded.get('accepts',[{}])[0], indent=2)[:500]}")
            ext = decoded.get("extensions",{})
            if ext:
                print(f"  extensions: {json.dumps(ext, indent=2)[:1000]}")
            else:
                print("  NO extensions in 402 response")
        print()
        print(f"  Top-level keys: {list(j.keys())}")
    except Exception as e:
        print(f"  parse err: {e}")
        print(f"  raw: {d[:500]}")

# 2) Look for x402 discovery sites
print()
print("=" * 60)
print("X402 DISCOVERY SITES")
print("=" * 60)
sites = [
    "https://x402.org/registry",
    "https://x402discovery.com",
    "https://echo.x402",
    "https://x402registry.com",
    "https://pay.x402",
    "https://x402pay.com",
    "https://list.x402",
    "https://x402list.com",
    "https://www.x402scan.com",
    "https://x402scan.com",
    "https://www.x402index.com",
    "https://x402index.com",
    "https://www.x402hub.com",
    "https://x402hub.com",
    "https://bazaar.x402",
    "https://x402bazaar.com",
    "https://x402directory.com",
    "https://www.x402directory.com",
    "https://x402.gallery",
    "https://www.x402.gallery",
]
for s2 in sites:
    s, d = fetch(s2, headers={"Accept":"text/html,application/json"}, timeout=8)
    if s in [200,301,302]:
        size = len(d) if isinstance(d, str) else len(json.dumps(d))
        print(f"  {s} {s2}  ({size}b)")
    elif s == -1:
        print(f"  ERR {s2}")

# 3) Check agentic.market v1/services GET - what does it return?
print()
print("=" * 60)
print("AGENTIC.MARKET: top services")
print("=" * 60)
s, d = fetch("https://api.agentic.market/v1/services?limit=10&offset=0",
             headers={"Accept":"application/json"})
if isinstance(d, dict):
    print(f"  total: {d.get('total')}")
    for s2 in d.get("services",[])[:10]:
        print(f"    {s2.get('name','')[:60]} | ${s2.get('price','?')}")
        print(f"      url: {s2.get('url','')[:80]}")
        if 'tags' in s2: print(f"      tags: {s2.get('tags')}")

# Search agentic.market for AI signals
print()
s, d = fetch("https://api.agentic.market/v1/services?search=ai+signal&limit=20",
             headers={"Accept":"application/json"})
if isinstance(d, dict):
    print(f"  search 'ai signal': total={d.get('total')}")
    for s2 in d.get("services",[])[:5]:
        print(f"    {s2.get('name','')[:60]}")
