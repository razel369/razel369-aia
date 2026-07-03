#!/usr/bin/env python3
"""POST to www.x402scan.com /api/resources/register (with proper redirect)."""
import json, urllib.request, urllib.error, re, base64

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
opener = urllib.request.build_opener(NoRedirect)

def fetch_full(url, headers=None, method="GET", data=None, timeout=20, follow=True):
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
        if follow:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                text = r.read().decode("utf-8", errors="replace")
                return r.status, dict(r.headers), text
        else:
            with opener.open(req, timeout=timeout) as r:
                text = r.read().decode("utf-8", errors="replace")
                return r.status, dict(r.headers), text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        return e.code, dict(e.headers), text
    except Exception as e:
        return -1, {}, str(e)

# 1) Try the www version
print("=" * 60)
print("x402scan www version - POST /api/resources/register")
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
    "/api/services/register",
    "/api/v1/resources/register",
    "/api/v1/resources",
    "/api/resources",
    "/api/services",
    "/api/v1/services/register",
    "/api/public/resources/register",
    "/api/public/services/register",
]:
    s, h, b = fetch_full(f"https://www.x402scan.com{path}", method="POST", data=service,
                         headers={"Accept":"application/json"})
    print(f"  {s} {path}")
    if isinstance(b, str) and len(b) < 1000:
        print(f"    {b[:500]}")

# 2) Try GET on /api/resources to see what fields it expects
print()
print("=" * 60)
print("x402scan GET /api/resources (schema discovery)")
print("=" * 60)
for path in [
    "/api/resources",
    "/api/services",
    "/api/v1/resources",
    "/api/v1/services",
    "/api/public/resources",
    "/api/public/services",
    "/api/resources/schema",
    "/api/services/schema",
]:
    s, h, b = fetch_full(f"https://www.x402scan.com{path}", method="GET",
                         headers={"Accept":"application/json"})
    if s == 200:
        print(f"  {s} {path}")
        if isinstance(b, str):
            print(f"    {b[:500]}")
    else:
        print(f"  {s} {path}")

# 3) Try with form data instead of JSON
print()
print("=" * 60)
print("x402scan POST /api/resources (form data)")
print("=" * 60)
form_data = urllib.parse.urlencode(service).encode("utf-8")
for path in ["/api/resources/register","/api/resources"]:
    req = urllib.request.Request(f"https://www.x402scan.com{path}", method="POST", data=form_data,
        headers={"Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            t = r.read().decode("utf-8", errors="replace")
            print(f"  {r.status} {path}: {t[:300]}")
    except urllib.error.HTTPError as e:
        t = e.read().decode("utf-8", errors="replace")
        print(f"  {e.code} {path}: {t[:300]}")
