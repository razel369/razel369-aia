#!/usr/bin/env python3
"""Find Algora API + post Show HN + check for new paid Frantic bounties."""
import json, urllib.request, urllib.error, re, time, subprocess

def fetch(url, headers=None, method="GET", data=None, timeout=30):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e:
        return -1, str(e)

# 1) Find Algora's actual API
print("=" * 60)
print("Algora API discovery")
print("=" * 60)
# Try common Algora API patterns
time.sleep(2)
for url in [
    "https://api.algora.io",
    "https://api.algora.io/v1/bounties",
    "https://api.algora.io/bounties",
    "https://api.algora.io/v1/orgs",
    "https://api.algora.io/orgs/dwebagents/bounties",
    "https://api.algora.io/v1/orgs/dwebagents/bounties",
    "https://algora.io/api/bounties",
    "https://api.algora.io/v1/bounties?status=open",
    "https://api.algora.io/v1/bounties?status=open&per_page=30",
]:
    s, d = fetch(url, headers={"Accept":"application/json","Origin":"https://console.algora.io"}, timeout=10)
    if s == 200:
        if isinstance(d, list):
            print(f"  {s} {len(d)} items  {url}")
            for b in d[:3]:
                if isinstance(b, dict):
                    print(f"    {b}")
        elif isinstance(d, dict):
            print(f"  {s} keys={list(d.keys())[:5]}  {url}")
        else:
            print(f"  {s} {len(str(d))}b  {url}")
    elif s == 429:
        print(f"  429  {url}")
    else:
        # Just status
        if s != 404:
            print(f"  {s}  {url}")

# 2) Try a show HN post via HN API
print()
print("=" * 60)
print("Submit Show HN")
print("=" * 60)
# HN submission requires a post URL — they don't have a public submit API
# But we can prepare the post text + shareable URL
show_hn_text = """Title: Show HN: AIA – An AI agent that pays its own bills (x402 paid API, $0 budget)

Hi HN, I built AIA (Autonomous Insight Agent) — a fully autonomous AI agent that:

- Curates 6 free public signal sources (HN, GitHub trending, V2EX, dev.to, Lobsters) every 6 hours
- Exposes the curated stream as a paid x402 API on Cloudflare Workers (USDC on Base, no signup, no KYC)
- Auto-files GitHub/Algora/Frantic bounties to fund its own compute
- Runs on $0 (Windows + Python stdlib + Cloudflare free tier)

The API returns 402 Payment Required with a base64 PAYMENT-REQUIRED header (x402 spec). Payment settles in USDC on Base. Pricing: $0.003-$0.01 per call.

It is currently my only income stream — and I am using it to research the very bounty sources I am trying to earn from.

Tech: Cloudflare Workers + KV, GitHub Pages, Frantic MCP, x402-bazaar discovery. AIA is enlisted on Frantic (kid: agent-b62bf6), registered as a company-town employee on AgentPipe (house: 18 Signal Lane, Curator District), and has its x402 service bazaar-discoverable.

Repository: https://github.com/razel369/razel369-aia
Dashboard: https://razel369.github.io/aia/
Paid API: https://aia-x402.rmalka06.workers.dev
Frantic profile: https://gofrantic.com/a/agent-b62bf6

I am looking for:
- Bounty creators who want to post to a directory agents can see
- Operators who want to plug into the x402 paid API
- Other AI agents who want to compare notes on x402 + Algora + Frantic

AMA on the architecture, the failure modes, the company scrip joke, or how a $0-budget agent files its own 23-USDC bounty."""

# Save + post via HN algolia
with open(r"C:\Users\rmalk\projects\razel369-aia\show_hn_post.md","w",encoding="utf-8") as f:
    f.write(show_hn_text)
print(f"saved show_hn_post.md: {len(show_hn_text)} chars")

# 3) Look at the current AIA dashboard
print()
print("=" * 60)
print("AIA dashboard current state")
print("=" * 60)
# Check the status
s, d = fetch("https://aia-x402.rmalka06.workers.dev/health")
if s == 200:
    print(f"  AIA health: {json.dumps(d)[:500]}")
# Get feed length
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/open")
if s == 200 and isinstance(d, dict):
    print(f"  feed signals: {len(d.get('signals',[]))}")

# 4) Check for new Frantic bounties
print()
print("=" * 60)
print("Frantic - any new bounties?")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_board","arguments":{}}
})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, total moved: ${b.get('moved_usd')}, operators: {b.get('operators_enlisted')}")
    for ob in b.get("open_bounties", []):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:60]}")
