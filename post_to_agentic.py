#!/usr/bin/env python3
"""Try to POST AIA to agentic.market + find submission endpoint."""
import json, urllib.request, urllib.error, re

# AIA service definition
AIA = {
  "id": "aia-x402",
  "name": "AIA — Autonomous Insight Agent",
  "description": "Filtered, curated AI/agent/crypto signal stream from 6 free public sources (HN, GitHub trending, V2EX, dev.to, Lobsters, GitHub repos). Pay per request, USDC on Base. JSON or plain-text digest.",
  "domain": "aia-x402.rmalka06.workers.dev",
  "provider": "razel369",
  "providerUrl": "https://razel369.github.io/aia/",
  "category": "Data",
  "networks": ["eip155:8453"],
  "endpoints": [
    {
      "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
      "description": "Filtered curated signal stream (JSON)",
      "pricing": {
        "amount": "0.01",
        "currency": "USDC",
        "network": "eip155:8453",
        "scheme": "exact",
        "maxAmount": "0.01",
        "minAmount": "0.01"
      },
      "method": "GET",
      "providerName": "razel369",
      "parameters": [
        {"group":"query","name":"topics","type":"string","description":"comma-separated topic filter","example":"ai-agents,x402,crypto","required":False},
        {"group":"query","name":"limit","type":"integer","description":"max signals to return","example":10,"required":False},
        {"group":"query","name":"min_score","type":"number","description":"minimum signal score","example":0,"required":False},
        {"group":"query","name":"source","type":"string","description":"source substring filter","example":"github","required":False},
      ],
      "serviceName": "AIA",
      "tags": ["ai","agents","signals","curation","news","crypto","x402","research"],
    },
    {
      "url": "https://aia-x402.rmalka06.workers.dev/v1/digest",
      "description": "One-paragraph daily digest (plain text)",
      "pricing": {
        "amount": "0.003",
        "currency": "USDC",
        "network": "eip155:8453",
        "scheme": "exact",
        "maxAmount": "0.003",
        "minAmount": "0.003"
      },
      "method": "GET",
      "providerName": "razel369",
      "parameters": [
        {"group":"query","name":"topics","type":"string","description":"comma-separated topic filter","example":"x402","required":False},
      ],
      "serviceName": "AIA",
      "tags": ["digest","summary","ai","agents","research"],
    },
    {
      "url": "https://aia-x402.rmalka06.workers.dev/v1/alerts",
      "description": "Webhook subscription preview (JSON list of matching signals)",
      "pricing": {
        "amount": "0.005",
        "currency": "USDC",
        "network": "eip155:8453",
        "scheme": "exact",
        "maxAmount": "0.005",
        "minAmount": "0.005"
      },
      "method": "GET",
      "providerName": "razel369",
      "parameters": [
        {"group":"query","name":"topics","type":"string","description":"topic to alert on","example":"crypto","required":False},
      ],
      "serviceName": "AIA",
      "tags": ["alerts","webhook","monitoring","ai","agents"],
    }
  ],
  "serviceName": "AIA",
  "tags": ["ai","agents","signals","curation","news","crypto","x402","research","autonomous"],
  "iconUrl": "https://razel369.github.io/aia/icon.png",
  "priceSummary": {
    "minAmount": "0.003",
    "maxAmount": "0.01",
    "avgCostPerTransaction": "0.006",
    "avgCostBasis": "exact",
    "currency": "USDC"
  }
}

# 1) Try POSTing to the API
print("=" * 60)
print("1. POST AIA to api.agentic.market/v1/services")
print("=" * 60)
for url in [
    "https://api.agentic.market/v1/services",
    "https://api.agentic.market/v1/services/register",
    "https://api.agentic.market/v1/register",
    "https://agentic.market/api/v1/services",
    "https://api.agentic.market/services",
]:
    try:
        req = urllib.request.Request(url, method="POST",
                                     data=json.dumps(AIA).encode("utf-8"),
                                     headers={
                                       "Content-Type":"application/json",
                                       "User-Agent":"razel369-aia/1.0",
                                       "Accept":"application/json"
                                     })
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"  {url} → {r.status}: {r.read().decode('utf-8', errors='replace')[:300]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200] if hasattr(e, 'read') else str(e)
        print(f"  {url} → {e.code}: {body}")
    except Exception as e:
        print(f"  {url} → err: {e}")

# 2) Look for the agentic.market GitHub repo (try various)
print()
print("=" * 60)
print("2. Search GitHub for agentic.market / x402 bazaar registry")
print("=" * 60)
import urllib.parse
for q in ["agentic.market", "x402 bazaar", "x402 registry", "x402 facilitator list"]:
    try:
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&sort=stars&order=desc"
        req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
            items = d.get("items", [])
            for it in items[:3]:
                print(f"  q={q!r:<25}  ★{it.get('stargazers_count',0):>6}  {it.get('full_name','')}  {it.get('description','')[:60]}")
    except Exception as e:
        print(f"  q={q!r:<25}  err: {e}")

# 3) Look for the "submit a service" mechanism on the agentic.market dashboard
print()
print("=" * 60)
print("3. Check agentic.market home page for forms / scripts / submit endpoints")
print("=" * 60)
try:
    req = urllib.request.Request("https://agentic.market", headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode("utf-8")
        # Find any action endpoints, form actions, api calls
        for kw in ["form", "action=", "POST", "/api/", "/v1/", "submit", "github", "twitter", "discord"]:
            matches = list(re.finditer(kw, body, re.IGNORECASE))
            if matches:
                m = matches[0]
                start = max(0, m.start()-50)
                end = min(len(body), m.end()+200)
                print(f"  '{kw}': ...{body[start:end].replace(chr(10),' ')[:200]}...")
except Exception as e:
    print(f"err: {e}")
