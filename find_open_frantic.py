#!/usr/bin/env python3
"""Find all OPEN postingStatus bounties (not just #49)."""
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

# Scan 1-200 and track postingStatus
print("=" * 60)
print("ALL FRANTIC BOUNTIES (1-200) — status check")
print("=" * 60)
statuses = {}
for bid in range(1, 201):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if b and isinstance(b, dict):
            ps = b.get("postingStatus","?")
            ws = b.get("workStatus","?")
            price = b.get("priceUsd") or 0
            title = (b.get("title") or "")[:50]
            if ps not in statuses: statuses[ps] = []
            statuses[ps].append((bid, price, ws, title))
    time.sleep(0.1)

print()
print("Status counts:")
for k, v in statuses.items():
    print(f"  {k}: {len(v)} bounties")

# Show all open/capable
print()
print("=" * 60)
print("OPEN BOUNTIES (postable)")
print("=" * 60)
for k in ["open","OPEN","reopen","REOPENED","post","POST","claim","CLAIM"]:
    for bid, price, ws, title in statuses.get(k, []):
        print(f"  #{bid} ${price} workStatus={ws} {title}")
        # Get full details
        s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
            headers={"Accept":"application/json, text/event-stream"},
            data={"jsonrpc":"2.0","id":1,"method":"tools/call",
                  "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
        if isinstance(d, dict):
            sc = d.get("result",{}).get("structuredContent",{})
            b2 = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
            cp = b2.get("claimProgress",{})
            print(f"        cap: {cp.get('capacity')}, avail: {cp.get('available')}, paid: {cp.get('paid')}")
            print(f"        desc: {b2.get('description','')[:300]}")

# Show all "closed" but check if capacity remaining
print()
print("=" * 60)
print("CLOSED WITH CAPACITY (check available slots)")
print("=" * 60)
for bid, price, ws, title in statuses.get("closed", [])[:30]:
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b2 = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        cp = b2.get("claimProgress",{})
        avail = cp.get("available", 0)
        cap = cp.get("capacity", 0)
        if cap > 1 or avail > 0:
            print(f"  #{bid} ${price} cap={cap} avail={avail} {title}")
