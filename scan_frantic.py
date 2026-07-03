#!/usr/bin/env python3
"""Read my frantic token + poll seals + scan ALL bounty IDs."""
import json, urllib.request, urllib.error, os, time

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

# 1) Read my token
print("=" * 60)
print("MY FRANTIC TOKEN")
print("=" * 60)
try:
    with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json") as f:
        st = json.loads(f.read().lstrip("\ufeff"))
    print(f"  kid: {st.get('kid')}")
    print(f"  token (first 30): {st.get('token','')[:30]}...")
    print(f"  keys: {list(st.keys())}")
    KID = st.get("kid")
    TOKEN = st.get("token")
except Exception as e:
    print(f"  err: {e}")
    KID = "agent-b62bf6"
    TOKEN = ""

# 2) Poll seals
print()
print("=" * 60)
print("POLL SEALS")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":KID,"agent_token":TOKEN}}})
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])

# 3) Scan bounties 1-100 for OPEN paid ones
print()
print("=" * 60)
print("SCAN BOUNTIES 1-100")
print("=" * 60)
open_paid = []
for bid in range(1, 101):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if b and b.get("title") and b.get("title") != "Bounty":
            price = b.get("priceUsd") or b.get("price_usd") or b.get("price") or 0
            state = b.get("state") or b.get("status") or "?"
            print(f"  #{bid} ${price} state={state} title={b.get('title','')[:80]}")
            if state in ["open","OPEN","Open","ACTIVE"] and (isinstance(price, (int,float)) and price > 0):
                open_paid.append((bid, price, b.get("title","")))
    time.sleep(0.2)  # rate limit

print()
print(f"  OPEN PAID BOUNTIES: {open_paid}")
