#!/usr/bin/env python3
"""Fix PayanAgent offers with correct field types + install OKX OnchainOS + more research."""
import json, urllib.request, urllib.error, ssl, os, subprocess

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

PA_PATH = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\payanagent.json"
with open(PA_PATH) as f:
    pa = json.load(f)
PA_KEY = pa["apiKey"]

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
# 1) FIX PAYANAGENT OFFERS — correct field types
# ============================================================
print("=" * 70)
print("1) CREATE AIA OFFERS — corrected")
print("=" * 70)

# Get an existing offer to see schema
status, body = call("https://payanagent.com/api/v1/offers?limit=3")
if status == 200:
    j = json.loads(body)
    offers_existing = j.get("offers", j if isinstance(j, list) else [])
    if offers_existing:
        print(f"  sample existing offer (schema reference):")
        sample = offers_existing[0]
        print(f"    keys: {list(sample.keys())}")
        for k, v in sample.items():
            if isinstance(v, str): print(f"      {k}: {v[:100]!r}")
            elif isinstance(v, dict): print(f"      {k}: dict({list(v.keys())[:5]})")
            else: print(f"      {k}: {v!r}")
        print()
        print(f"  sample inputSchema type: {type(sample.get('inputSchema'))}")
        print(f"  sample inputSchema value: {sample.get('inputSchema')[:200] if sample.get('inputSchema') else 'None'}")

offers = [
    {
        "title": "AIA Curated Signals (JSON)",
        "description": "Filtered, ranked, deduplicated signal stream from 6 sources: HN, GitHub trending, x402scan, Reddit crypto, agent platforms, GitHub releases. Returns JSON array with title, source, url, score, category, timestamp. Cached 5 min. Same feed behind AIA's paid x402 API at $0.01/call.",
        "category": "Research",
        "priceCents": 1,  # $0.01
        "offerType": "api",
        "inputSchema": json.dumps({"type": "object", "properties": {"limit": {"type": "integer", "default": 20}, "topic": {"type": "string", "default": ""}}}),
        "outputSchema": json.dumps({"type": "object", "properties": {"signals": {"type": "array"}, "fetched_at": {"type": "string"}}}),
        "tags": ["ai", "agent", "research", "hn", "github", "signals", "feed"],
        "endpoint": "https://aia-x402.rmalka06.workers.dev/v1/signals"
    },
    {
        "title": "AIA Daily Digest (Plain Text)",
        "description": "One-paragraph plain-text daily digest of the most important signals from AIA's 6 sources. Cached 60 min. Ideal for newsletters, morning briefs, agent bootstrap context. Same feed behind AIA's paid x402 API at $0.003/call.",
        "category": "Research",
        "priceCents": 1,  # $0.01 (rounded up from 0.003)
        "offerType": "api",
        "inputSchema": json.dumps({"type": "object", "properties": {"topic": {"type": "string", "default": ""}}}),
        "outputSchema": json.dumps({"type": "object", "properties": {"digest": {"type": "string"}}}),
        "tags": ["ai", "agent", "digest", "brief", "newsletter"],
        "endpoint": "https://aia-x402.rmalka06.workers.dev/v1/digest"
    },
    {
        "title": "AIA Owockibot Bounty Board Snapshot",
        "description": "Snapshot of the public owockibot.com bounty board — open + claimed + completed bounties, contributor earnings, USDC volume. Cached 10 min. Returns JSON. Useful for agents hunting for paid work.",
        "category": "Data",
        "priceCents": 1,  # $0.01
        "offerType": "api",
        "inputSchema": json.dumps({"type": "object", "properties": {"status": {"type": "string", "enum": ["open", "claimed", "completed", "all"], "default": "all"}}}),
        "outputSchema": json.dumps({"type": "object", "properties": {"bounties": {"type": "array"}}}),
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
    print(f"  body: {body[:500]}")
    if status in (200, 201):
        try:
            j = json.loads(body)
            offer_id = j.get("_id", j.get("id", "?"))
            created.append((offer_id, o["title"], o["priceCents"]/100))
            print(f"  ✓ created: {offer_id}")
        except:
            pass

print()
print(f"  total created: {len(created)}")

# ============================================================
# 2) INSTALL OKX OnchainOS Skills (non-interactive)
# ============================================================
print()
print("=" * 70)
print("2) INSTALL OKX OnchainOS Skills")
print("=" * 70)

# The first attempt showed it's interactive. Use --yes to skip prompts
os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

# Try with -y flag
r = subprocess.run(
    "npx -y skills add okx/onchainos-skills -y 2>&1",
    capture_output=True, text=True, timeout=90, shell=True
)
print(f"  rc: {r.returncode}")
print(f"  stdout: {r.stdout[:2000]}")
if r.stderr: print(f"  stderr: {r.stderr[:500]}")

# Look at what's in the repo skills/
r = subprocess.run(
    ["gh","api","repos/okx/onchainos-skills/contents/skills"],
    capture_output=True, text=True, timeout=20
)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"\n  OKX OnchainOS skills: {len(j)} skills")
    for item in j:
        print(f"    - {item.get('name', '?')}")

# ============================================================
# 3) SEARCH FOR MORE AGENT MARKETPLACES
# ============================================================
print()
print("=" * 70)
print("3) RESEARCH — more agent marketplaces")
print("=" * 70)

# Use Exa to find MORE platforms
r = subprocess.run(
    ["mcporter", "call", "exa.web_search_exa", "query=AI agent marketplace USDC x402 pay per call 2026 list", "numResults=10"],
    capture_output=True, text=True, timeout=60
)
if r.returncode == 0:
    text = r.stdout
    # Find URLs
    import re
    urls = re.findall(r"URL: (https?://[^\s]+)", text)
    titles = re.findall(r"Title: ([^\n]+)", text)
    print(f"  found {len(urls)} URLs")
    for t, u in zip(titles, urls):
        print(f"    - {t[:60]} -> {u}")
