#!/usr/bin/env python3
"""List all VISIBLE Frantic bounties with full details + capacity."""
import json, urllib.request, urllib.error, time

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

print("=" * 60)
print("ALL VISIBLE FRANTIC BOUNTIES")
print("=" * 60)
visible = []
for bid in range(1, 201):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if b and isinstance(b, dict) and b.get("postingStatus") == "visible":
            visible.append((bid, b))
    time.sleep(0.1)

# Sort by price desc
visible.sort(key=lambda x: -(x[1].get("priceUsd") or 0))
print(f"  found: {len(visible)} visible bounties")
for bid, b in visible:
    price = b.get("priceUsd") or 0
    title = (b.get("title") or "")[:80]
    cp = b.get("claimProgress",{})
    cap = cp.get("capacity", 0)
    avail = cp.get("available", 0)
    ws = b.get("workStatus","?")
    print()
    print(f"  #{bid} ${price} cap={cap} avail={avail} ws={ws} {title}")
    print(f"      desc: {b.get('description','')[:400]}")
    print(f"      claim_window: {b.get('claimWindowMinutes')}")
    print(f"      criteria: {b.get('criteria')}")
    print(f"      routes: {b.get('completionRoutes')}")
    print(f"      required_artifacts: {b.get('requiredArtifacts')}")
    print(f"      url: {b.get('url')}")
