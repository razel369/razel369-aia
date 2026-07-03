#!/usr/bin/env python3
"""Check Cloudflare analytics: request count, errors, traffic."""
import json, urllib.request, ssl, urllib.error
import subprocess, os

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}

# Cloudflare Analytics API
# Account ID needed - try workers.cloudflare.com analytics endpoint
# Or use the wrangler tail logs (we know worker name is aia-x402)

# Try Cloudflare API directly: Account ID from env or wrangler
ACCOUNT_ID = "rmalka06"  # likely the account identifier
ZONE_ID = None  # workers.dev zone

# Try Cloudflare API for worker analytics
print("--- Cloudflare API worker analytics ---")
# Account ID for rmalka06@gmail.com — try common patterns
for account_id in ["rmalka06", "rmalka06-llc", "e6a6f3d1c8a44e3a9b5b9b5b5b5b5b5b"]:
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/analytics?worker=aia-x402&since=2026-07-01"
    print(f"  trying {url[:80]}...")
    # Without auth this won't work — skip

# Try the Cloudflare Workers Logs API endpoint
# https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{script_name}/logs

# Use wrangler via subprocess (PowerShell shim)
print()
print("--- wrangler analytics ---")
# Need to be in worker dir
os.chdir(r"C:\Users\rmalk\projects\razel369-aia\cloudflare-worker")
r = subprocess.run(
    ["C:\\Users\\rmalk\\AppData\\Roaming\\npm\\wrangler.ps1", "deployments", "list"],
    capture_output=True, text=True, timeout=30, shell=True
)
print(f"  rc={r.returncode}")
print(f"  out: {r.stdout[:500]}")
if r.stderr: print(f"  err: {r.stderr[:300]}")

# Try wrangler whoami for account info
print()
print("--- wrangler whoami ---")
r = subprocess.run(
    ["C:\\Users\\rmalk\\AppData\\Roaming\\npm\\wrangler.ps1", "whoami"],
    capture_output=True, text=True, timeout=30, shell=True
)
print(f"  out: {r.stdout[:500]}")

# Hit AIA worker 5 times to confirm it serves
print()
print("--- AIA worker live test (5 hits) ---")
for i in range(5):
    req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/health", headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        body = r.read().decode()
        j = json.loads(body)
        print(f"  hit {i+1}: status={r.status} ts={j.get('ts')}")
