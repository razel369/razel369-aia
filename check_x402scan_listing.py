#!/usr::usr/env python3
"""Look at x402scan search page for razel369 to find what's there + set up Frantic high-freq poll."""
import json, urllib.request, urllib.error, re, time, os

def fetch(url, headers=None, method="GET", data=None, timeout=20):
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

# 1) x402scan search for razel369
print("=" * 60)
print("x402scan search razel369 — what mentions exist?")
print("=" * 60)
s, d = fetch("https://www.x402scan.com/resources?q=razel369")
if isinstance(d, str):
    # Find all matches
    for m in re.finditer(r'razel369|rmalka06|aia-x402', d, re.IGNORECASE):
        ctx_start = max(0, m.start() - 100)
        ctx_end = min(len(d), m.end() + 100)
        ctx = d[ctx_start:ctx_end].replace("\n", " ")
        print(f"  match: ...{ctx[:200]}...")

# 2) Look at a specific service on x402scan to see the schema
print()
print("=" * 60)
print("x402scan single service page (find example)")
print("=" * 60)
s, d = fetch("https://www.x402scan.com")
if isinstance(d, str):
    # Find service IDs and example URLs
    for m in re.finditer(r'/resources/svc_[a-z0-9]+', d):
        print(f"  example: https://www.x402scan.com{m.group(0)}")
        break
    # Look for any link to a service
    for m in re.finditer(r'href="(/resources/[^"]+)"', d):
        print(f"  link: {m.group(1)[:100]}")

# 3) Set up Frantic polling — record current state then watch for new paid bounties
print()
print("=" * 60)
print("FRANTIC: snapshot current state + start watching")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    snapshot = {
        "open_count": b.get("bounties_open"),
        "moved": b.get("moved_usd"),
        "feed_count": len(b.get("feed",[])),
        "last_event_at": b.get("feed",[{}])[0].get("at") if b.get("feed") else None,
        "snapshot_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    print(f"  snapshot: {json.dumps(snapshot)}")
    # Save snapshot for high-freq poll comparison
    with open("frantic_snapshot.json", "w") as f:
        json.dump(snapshot, f)
    # Also save list of paid bounties
    paid = []
    for ob in b.get("open_bounties",[]):
        paid.append({"number": ob.get("number"), "price": ob.get("price_usd"), "title": ob.get("title")})
    with open("frantic_open.json", "w") as f:
        json.dump({"open_bounties": paid, "captured": time.time()}, f)
    print(f"  open paid: {paid}")
    # Watch the feed for new events
    print()
    print("  Recent feed (top 15):")
    for e in b.get("feed",[])[:15]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:120]}")

# 4) Find x402 Discord (deep look)
print()
print("=" * 60)
print("x402 DISCORD INFO")
print("=" * 60)
s, d = fetch("https://www.x402scan.com", headers={"Accept":"text/html"})
if isinstance(d, str):
    for m in re.finditer(r'discord(?:\.gg|app\.com)[/a-zA-Z0-9_-]+', d, re.IGNORECASE):
        print(f"  {m.group(0)}")
    for m in re.finditer(r'telegram\.me/([a-zA-Z0-9_-]+)', d, re.IGNORECASE):
        print(f"  telegram: {m.group(1)}")
    for m in re.finditer(r't\.me/([a-zA-Z0-9_-]+)', d, re.IGNORECASE):
        print(f"  t.me: {m.group(1)}")

# 5) Look at x402.org
print()
print("=" * 60)
print("x402.org — main site")
print("=" * 60)
for path in ["/", "/facilitator", "/services", "/registry", "/docs", "/community"]:
    s, d = fetch(f"https://x402.org{path}")
    if isinstance(d, str) and s == 200:
        print(f"  {s} {path}  ({len(d)}b)")
