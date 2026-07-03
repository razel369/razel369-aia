#!/usr/bin/env python3
"""Scan Frantic bounties 200-500 + try to find one that's claimable + drive AIA x402 traffic."""
import json, urllib.request, urllib.error, time, os, subprocess

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

# 1) Scan bounties 200-500 for paid + open
print("=" * 60)
print("SCAN FRANTIC 200-500")
print("=" * 60)
paid_open = []
for bid in range(200, 501):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if b and isinstance(b, dict) and b.get("title") and b.get("title") != "Bounty":
            ps = b.get("postingStatus","?")
            ws = b.get("workStatus","?")
            price = b.get("priceUsd") or 0
            cp = b.get("claimProgress",{})
            avail = cp.get("available", 0)
            cap = cp.get("capacity", 0)
            if (avail > 0 and price > 0):
                paid_open.append((bid, price, ps, ws, avail, cap, b.get("title","")))
                print(f"  *** #{bid} ${price} avail={avail}/{cap} {b.get('title','')[:70]}")
            elif price > 0:
                # Show some paid ones for context
                pass
    time.sleep(0.1)
    if bid % 50 == 0:
        print(f"  ... scanned {bid}")

print()
print(f"  TOTAL CLAIMABLE PAID: {len(paid_open)}")
for bid, price, ps, ws, avail, cap, title in paid_open:
    print(f"  #{bid} ${price} avail={avail}/{cap} {title[:70]}")

# 2) Check AIA x402 activity
print()
print("=" * 60)
print("AIA X402 WORKER HEALTH")
print("=" * 60)
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/signals")
print(f"  status: {s}")
if isinstance(d, dict):
    print(f"  keys: {list(d.keys())[:5]}")
print()
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/digest")
print(f"  /v1/digest status: {s}")
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/alerts")
print(f"  /v1/alerts status: {s}")
