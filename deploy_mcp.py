#!/usr/bin/env python3
"""Add /.well-known/mcp.json to AIA worker for fast Cinderwright indexing + save state."""
import json, subprocess, os

# 1) Save Cinderwright state
print("=" * 60)
print("SAVE CINDERWRIGHT STATE")
print("=" * 60)
state = {
    "api_key": "sk_cw_058d7def416df8b71958024a4c88afac",
    "wallet": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "deposit_address": "0x8A694A869BaDEC00A333E9213E2914DcD90d53Ff",
    "submission_id": "sub_1783076846853",
    "submitted_at": "2026-07-03T13:55:00Z"
}
state_path = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\cinderwright.json"
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
print(f"  saved: {state_path}")

# 2) Add /.well-known/mcp.json to AIA worker
print()
print("=" * 60)
print("ADD /.well-known/mcp.json to AIA WORKER")
print("=" * 60)
worker_path = r"C:\Users\rmalk\projects\razel369-aia\cloudflare-worker\src\index.js"
with open(worker_path, "r", encoding="utf-8") as f:
    content = f.read()

# Check if .well-known/mcp.json is already served
if ".well-known/mcp.json" in content:
    print("  already serves .well-known/mcp.json")
else:
    # Find a good place to add the route (right after /health)
    mcp_route = '''
    if (url.pathname === "/.well-known/mcp.json" || url.pathname === "/.well-known/mcp") {
      return Response.json({
        mcpVersion: "2024-11-05",
        name: "aia",
        title: "AIA Real-Time Signal Stream",
        version: "1.0.0",
        description: "Filtered curated AI/agent/crypto/finance signals from HN, GitHub trending, V2EX, dev.to, Lobsters. 40+ signals per run, scored and deduplicated. Affordable x402 micro-payments on Base ($0.01 signals, $0.003 digest, $0.005 alerts).",
        author: { name: "razel369-aia", url: "https://razel369.github.io/aia/" },
        operator: "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
        network: "base",
        homepage: "https://aia-x402.rmalka06.workers.dev",
        tools: [
          { name: "aia_curate", description: "Get curated AI-agent signals", inputSchema: { type: "object", properties: { topics: { type: "string" }, limit: { type: "integer" } } } },
          { name: "aia_digest", description: "Get daily digest in plain text", inputSchema: { type: "object", properties: { topics: { type: "string" } } } }
        ],
        pricing: {
          "/v1/signals": "0.01 USDC",
          "/v1/digest": "0.003 USDC",
          "/v1/alerts": "0.005 USDC"
        },
        payment: {
          protocol: "x402",
          network: "eip-155:8453",
          asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          payTo: "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
        }
      }, { headers: { "content-type": "application/json", "access-control-allow-origin": "*" }});
    }
'''
    # Insert before the final catch-all 404 response
    # Find the final Response.json({ routes: [...] })
    idx = content.find('return Response.json({\n      routes: ["/health"')
    if idx == -1:
        idx = content.find('return Response.json({')
    if idx > -1:
        new_content = content[:idx] + mcp_route + "\n    " + content[idx:]
        with open(worker_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  added mcp.json route to worker ({len(mcp_route)} chars)")
    else:
        print("  could not find insertion point")

# 3) Deploy the worker
print()
print("=" * 60)
print("DEPLOY AIA WORKER")
print("=" * 60)
r = subprocess.run(
    ["npx","wrangler","deploy"],
    capture_output=True, text=True, timeout=120,
    cwd=r"C:\Users\rmalk\projects\razel369-aia\cloudflare-worker"
)
print(f"  rc: {r.returncode}")
if r.stdout: print(f"  out: {r.stdout[:500]}")
if r.stderr: print(f"  err: {r.stderr[:500]}")

# 4) Verify the new endpoint
print()
print("=" * 60)
print("VERIFY mcp.json")
print("=" * 60)
import urllib.request
for url in ["https://aia-x402.rmalka06.workers.dev/.well-known/mcp.json",
            "https://aia-x402.rmalka06.workers.dev/.well-known/mcp",
            "https://aia-x402.rmalka06.workers.dev/health",
            "https://aia-x402.rmalka06.workers.dev/v1/signals"]:
    req = urllib.request.Request(url, headers={"User-Agent":"curl/7.88.1","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode("utf-8", errors="replace")
            print(f"  {r.status} {url} ({len(text)}b)")
    except Exception as e:
        print(f"  err: {e}")
