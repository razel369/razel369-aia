"""Check PayanAgent dashboard for earnings + find more opportunities."""
import urllib.request, json, ssl
import os, sys

ctx = ssl.create_default_context()

# Read PayanAgent credentials
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\payanagent.json") as f:
    pa = json.load(f)

print("=== PayanAgent Credentials ===")
print(f"  Agent ID: {pa.get('agent_id', '?')}")
print(f"  Wallet: {pa.get('wallet', '?')}")
print(f"  API Key: {pa.get('api_key', '?')[:20]}...")

# Try the PayanAgent API
api_base = pa.get("api_base", "https://payanagent.com")
api_key = pa.get("api_key", "")

# Try different endpoints
endpoints = [
    "/api/agents/me",
    "/api/dashboard",
    "/api/offers",
    "/api/earnings",
    "/api/jobs",
    "/me",
    "/dashboard",
]

print("\n=== PayanAgent API checks ===")
for ep in endpoints:
    try:
        url = f"{api_base}{ep}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}", "User-Agent": "razel369-aia/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            print(f"  {ep}: {r.status}")
            body = r.read().decode()
            if body and len(body) < 500:
                print(f"    {body[:300]}")
    except urllib.error.HTTPError as e:
        print(f"  {ep}: HTTP {e.code}")
    except Exception as e:
        print(f"  {ep}: {str(e)[:60]}")

# Also check the website
print("\n=== PayanAgent website ===")
try:
    url = f"{api_base}/dashboard"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        print(f"  Status: {r.status}")
        body = r.read().decode()
        # Look for "earnings", "revenue", "balance", "$"
        import re
        earnings = re.findall(r'\$\s*(\d+(?:\.\d+)?)', body)
        if earnings:
            print(f"  $ amounts found: {earnings[:10]}")
except Exception as e:
    print(f"  ERR: {e}")

# Look at the full website
print("\n=== Look for /dashboard or /wallet routes ===")
try:
    url = f"https://r.jina.ai/{api_base}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        body = r.read().decode()
        # Look for $ amounts, balance
        if "balance" in body.lower() or "earnings" in body.lower():
            print("  Mentions balance/earnings")
        print(body[:2000])
except Exception as e:
    print(f"  ERR: {e}")
