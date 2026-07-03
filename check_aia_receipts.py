#!/usr/bin/env python3
"""Check AIA x402 receipts — has anyone called the paid endpoints?"""
import json, urllib.request, ssl, urllib.error

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}

# 1) Health
print("--- AIA /health ---")
req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/health", headers=HEADERS)
with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
    body = r.read().decode()
    print(f"  status: {r.status}")
    j = json.loads(body)
    for k, v in j.items():
        print(f"    {k}: {v}")

# 2) Call /v1/signals to see if anyone has paid (it returns 402 = payment required)
print()
print("--- AIA /v1/signals (no payment) ---")
req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/v1/signals", headers=HEADERS)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        body = r.read().decode()
        print(f"  status: {r.status} (should be 200 if we paid, 402 if not)")
        print(f"  body[:300]: {body[:300]}")
except urllib.error.HTTPError as e:
    print(f"  status: {e.code}")
    body = e.read().decode()
    print(f"  body[:600]: {body[:600]}")

# 3) Call /v1/digest to see if anyone paid
print()
print("--- AIA /v1/digest (no payment) ---")
req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/v1/digest", headers=HEADERS)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        body = r.read().decode()
        print(f"  status: {r.status}")
        print(f"  body[:300]: {body[:300]}")
except urllib.error.HTTPError as e:
    print(f"  status: {e.code}")
    body = e.read().decode()
    print(f"  body[:600]: {body[:600]}")

# 4) Check x402.org facilitator for receipts (if any)
print()
print("--- x402.org facilitator ---")
req = urllib.request.Request("https://x402.org/facilitator/health", headers=HEADERS)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        body = r.read().decode()
        print(f"  status: {r.status}")
        print(f"  body[:300]: {body[:300]}")
except Exception as e:
    print(f"  ERR: {e}")

# 5) Check Cloudflare analytics via wrangler
import subprocess
r = subprocess.run(["C:\\Users\\rmalk\\AppData\\Roaming\\npm\\wrangler.ps1", "tail", "aia-x402"],
                   capture_output=True, text=True, timeout=30)
print()
print("--- wrangler tail ---")
if r.returncode == 0:
    print(r.stdout[:2000])
else:
    print(f"  rc={r.returncode}")
    print(f"  err: {r.stderr[:500]}")
