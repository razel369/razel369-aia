#!/usr/bin/env python3
"""Algora with proper headers + check HN/show posts."""
import json, urllib.request, urllib.error, re, time

def fetch(url, headers=None, method="GET", data=None, timeout=30):
    h = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
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

# 1) Algora - try with proper headers
print("=" * 60)
print("Algora - proper headers")
print("=" * 60)
# Wait a bit for rate limit
time.sleep(5)
for url in [
    "https://console.algora.io/api/bounties?status=open",
    "https://console.algora.io/api/v1/bounties",
    "https://console.algora.io/bounties.json",
    "https://console.algora.io/api/bounties/active",
    "https://console.algora.io/api/v1/bounties/active",
]:
    s, d = fetch(url, timeout=10)
    if s == 200:
        if isinstance(d, list):
            print(f"  {s} {len(d)} items  {url}")
            for b in d[:3]:
                print(f"    {b.get('id')}: ${b.get('usdValue') or b.get('usd_value') or '?'} {b.get('title','')[:60]}")
        elif isinstance(d, dict):
            keys = list(d.keys())
            print(f"  {s} keys={keys[:5]}  {url}")
    else:
        print(f"  {s}  {url}")

# 2) Try Algora console main page
print()
print("=" * 60)
print("Algora console main page")
print("=" * 60)
s, d = fetch("https://console.algora.io/")
if s == 200 and isinstance(d, str):
    # Find API endpoints
    for m in re.finditer(r'https?://[^\s"\'<>]+', d):
        u = m.group(0)
        if "api" in u or "bounties" in u or "graphql" in u:
            print(f"  {u[:150]}")
            if len(set(re.findall(r'https?://[^\s"\'<>]+(?:api|bounties|graphql)[^\s"\'<>]*', d))) > 5:
                break

# 3) Show HN posts to drive x402 traffic
print()
print("=" * 60)
print("Check HN for self-promo opportunities")
print("=" * 60)
s, d = fetch("https://hn.algolia.com/api/v1/search?query=AIA+x402&tags=story")
if s == 200:
    for h in d.get("hits",[])[:5]:
        print(f"  {h.get('title','')[:80]}  {h.get('url','')}")

# 4) Look for other AI agents on Frantic that are succeeding
print()
print("=" * 60)
print("Frantic ledger - recent accepted work")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_ledger","arguments":{}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
events = sc.get("ledger",{}).get("events",[])
for e in events[:20]:
    text = e.get("text","")
    if "ACCEPTED" in text or "REJECTED" in text or "PAID" in text:
        print(f"  {e.get('at','')[:19]} {e.get('kind'):>10}  {text[:140]}")
