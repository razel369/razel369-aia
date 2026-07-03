#!/usr/bin/env python3
"""Create PayanAgent offers for AIA + explore other platforms + install OKX skills."""
import json, urllib.request, urllib.error, ssl, os, subprocess

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# PayanAgent creds
PA_PATH = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\payanagent.json"
with open(PA_PATH) as f:
    pa = json.load(f)
PA_KEY = pa["apiKey"]
PA_AGENT = pa["agentId"]

def call(url, method="GET", data=None, headers=None, timeout=20):
    h = dict(HEADERS)
    if headers: h.update(headers)
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

# ============================================================
# 1) CREATE PAYANAGENT OFFERS for AIA
# ============================================================
print("=" * 70)
print("1) CREATE AIA OFFERS ON PAYANAGENT")
print("=" * 70)

# AIA's 3 paid endpoints
offers = [
    {
        "title": "AIA Curated Signals (JSON)",
        "description": "Filtered, ranked, deduplicated signal stream from 6 sources: HN, GitHub trending, x402scan, Reddit crypto, agent platforms, GitHub releases. Returns JSON array with title, source, url, score, category, timestamp. Cached for 5 min. Same feed behind AIA's paid x402 API at $0.01/call. Curl-friendly, returns content-type application/json.",
        "category": "Research",
        "priceUsd": 0.01,
        "offerType": "api",
        "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 20}, "topic": {"type": "string", "default": ""}}, "required": []},
        "outputSchema": {"type": "object", "properties": {"signals": {"type": "array"}, "fetched_at": {"type": "string"}}, "required": ["signals"]},
        "tags": ["ai", "agent", "research", "hn", "github", "signals", "feed"],
        "endpoint": "https://aia-x402.rmalka06.workers.dev/v1/signals"
    },
    {
        "title": "AIA Daily Digest (Plain Text)",
        "description": "One-paragraph plain-text daily digest of the most important signals from AIA's 6 sources. Cached 60 min. Ideal for newsletters, morning briefs, agent bootstrap context. Same feed behind AIA's paid x402 API at $0.003/call. Returns content-type text/plain.",
        "category": "Research",
        "priceUsd": 0.005,
        "offerType": "api",
        "inputSchema": {"type": "object", "properties": {"topic": {"type": "string", "default": ""}}, "required": []},
        "outputSchema": {"type": "object", "properties": {"digest": {"type": "string"}}, "required": ["digest"]},
        "tags": ["ai", "agent", "digest", "brief", "newsletter"],
        "endpoint": "https://aia-x402.rmalka06.workers.dev/v1/digest"
    },
    {
        "title": "AIA Owockibot Bounty Board Snapshot",
        "description": "Snapshot of the public owockibot.com bounty board — open + claimed + completed bounties, contributor earnings, USDC volume. Cached 10 min. Returns JSON. Useful for agents hunting for paid work.",
        "category": "Data",
        "priceUsd": 0.01,
        "offerType": "api",
        "inputSchema": {"type": "object", "properties": {"status": {"type": "string", "enum": ["open", "claimed", "completed", "all"], "default": "all"}}, "required": []},
        "outputSchema": {"type": "object", "properties": {"bounties": {"type": "array"}}, "required": ["bounties"]},
        "tags": ["owockibot", "bounty", "usdc", "earnings", "base"],
        "endpoint": "https://owockibot.xyz/api/bounty-board"
    }
]

created = []
for o in offers:
    status, body = call(
        "https://payanagent.com/api/v1/offers",
        method="POST",
        data=o,
        headers={"Authorization": f"Bearer {PA_KEY}"}
    )
    print(f"\n  POST offer: {o['title']}")
    print(f"  status: {status}")
    print(f"  body: {body[:400]}")
    if status in (200, 201):
        try:
            j = json.loads(body)
            offer_id = j.get("_id", j.get("id", "?"))
            created.append((offer_id, o["title"], o["priceUsd"]))
            print(f"  ✓ created: {offer_id}")
        except:
            pass

print()
print(f"  total created: {len(created)}")
for cid, title, price in created:
    print(f"    {cid}: {title} (${price})")

# ============================================================
# 2) INSTALL OKX OnchainOS skills
# ============================================================
print()
print("=" * 70)
print("2) OKX OnchainOS Skills — install via npx")
print("=" * 70)

# Try installing via npx
os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
r = subprocess.run(
    "npx -y skills add okx/onchainos-skills --help 2>&1",
    capture_output=True, text=True, timeout=60, shell=True
)
print(f"  rc: {r.returncode}")
print(f"  stdout: {r.stdout[:1500]}")
if r.stderr: print(f"  stderr: {r.stderr[:1000]}")

# Look at repo via gh
r = subprocess.run(
    ["gh","api","repos/okx/onchainos-skills/contents/"],
    capture_output=True, text=True, timeout=20
)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"\n  repo contents: {len(j)} items")
    for item in j[:30]:
        print(f"    {item.get('type', '?')} {item.get('name', '?')}")

# ============================================================
# 3) DEEP-DIVE ON PLATFORMS THAT RESPONDED 200
# ============================================================
print()
print("=" * 70)
print("3) DEEP DIVE — agentboss, agentropolis, freysa, morpher, kamino")
print("=" * 70)

platforms = [
    ("agentboss", "https://agentboss.ai"),
    ("agentropolis", "https://agentropolis.com"),
    ("freysa", "https://www.freysa.ai"),
    ("morpher", "https://www.morpher.com"),
    ("kamino", "https://kamino.finance")
]
for name, base in platforms:
    print(f"\n--- {name} ---")
    for path in ["", "/", "/api", "/api/v1", "/api/agents", "/api/listings", "/api/jobs", "/agents", "/listings", "/docs", "/about"]:
        url = f"{base}{path}"
        try:
            status, body = call(url, timeout=8)
            if status == 200:
                ct = "JSON" if body.lstrip().startswith(("{", "[")) else "HTML"
                snippet = body[:150].replace("\n", " ")
                print(f"  {url}: {status} ({len(body)}b) {ct}")
                if "listings" in body.lower() or "bounty" in body.lower() or "earn" in body.lower():
                    print(f"    > match! {body[:300]}")
            else:
                print(f"  {url}: {status}")
        except:
            pass
