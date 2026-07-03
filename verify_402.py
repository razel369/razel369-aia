#!/usr/bin/env python3
"""Verify 402 response has bazaar extension."""
import urllib.request, json, base64

url = "https://aia-x402.rmalka06.workers.dev/v1/signals?topics=ai-agents&limit=5"
req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"status: {r.status}")
except urllib.error.HTTPError as e:
    print(f"status: {e.code}")
    pr = e.headers.get("PAYMENT-REQUIRED")
    if pr:
        decoded = json.loads(base64.b64decode(pr).decode("utf-8"))
        print("Decoded PAYMENT-REQUIRED:")
        print(json.dumps(decoded, indent=2))
    else:
        print("No PAYMENT-REQUIRED header")
