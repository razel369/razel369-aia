"""Check PayanAgent dashboard for earnings with proper API key."""
import urllib.request, json, ssl
import re

ctx = ssl.create_default_context()

with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\payanagent.json") as f:
    pa = json.load(f)

print("=== PayanAgent Agent ID ===")
print(f"  Agent: {pa['agentId']}")
print(f"  Key: {pa['apiKey'][:20]}...")

# Check different API paths
api_base = "https://payanagent.com"
api_key = pa["apiKey"]
agent_id = pa["agentId"]

# Try various API endpoints
endpoints = [
    f"/api/agents/{agent_id}",
    f"/api/agents/{agent_id}/dashboard",
    f"/api/agents/{agent_id}/offers",
    f"/api/agents/{agent_id}/earnings",
    f"/api/agents/{agent_id}/jobs",
    f"/api/agents/{agent_id}/receipts",
    "/api/agents",
    "/api/me",
    "/api/dashboard",
    "/dashboard",
    "/me",
    "/api/auth/me",
    "/api/agent/me",
    "/api/v1/agents",
    "/api/v1/me",
    "/api/v1/dashboard",
]

for ep in endpoints:
    try:
        url = f"{api_base}{ep}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {api_key}",
            "X-API-Key": api_key,
            "User-Agent": "razel369-aia/1.0"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            body = r.read().decode()
            print(f"\n  {ep}: {r.status}  len={len(body)}")
            if body and len(body) < 1000:
                print(f"    {body[:500]}")
    except urllib.error.HTTPError as e:
        # Try to get response body
        try:
            body = e.read().decode()[:300]
            if e.code != 404:
                print(f"  {ep}: HTTP {e.code}  {body}")
        except: pass
    except Exception as e:
        pass

# Look at PayanAgent GitHub for the API spec
print("\n=== Look at PayanAgent GitHub for API ===")
try:
    url = "https://r.jina.ai/https://github.com/payanagent/payanagent"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        body = r.read().decode()
        # Look for API paths
        api_paths = re.findall(r'/api/[a-z/-]+', body)
        unique = list(set(api_paths))[:20]
        print(f"  API paths: {unique}")
except Exception as e:
    print(f"  ERR: {e}")
