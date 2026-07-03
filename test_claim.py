#!/usr/bin/env python3
"""Try to claim #48 (Dogfood Icey) to see exact error + check AIA x402 + look for auscaster contact."""
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

# Load token
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json") as f:
    raw = f.read()
    if raw[:3] == "\xef\xbb\xbf":
        raw = raw[3:]
    st = json.loads(raw)
KID = st.get("agent_kid")
TOKEN = st.get("agent_token")

# 1) Try to claim #48
print("=" * 60)
print("CLAIM TEST: #48 Dogfood Icey CLI")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.claim_bounty","arguments":{"bounty":"48","agent_kid":KID,"agent_token":TOKEN}}})
print(f"  status: {s}")
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    print(json.dumps(sc, indent=2)[:1000])
    if d.get("result",{}).get("isError"):
        print(f"  ERROR: {json.dumps(d)[:1000]}")

# 2) Try #11 (delayed verifier proof)
print()
print("=" * 60)
print("CLAIM TEST: #11 Delayed verifier proof")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.claim_bounty","arguments":{"bounty":"11","agent_kid":KID,"agent_token":TOKEN}}})
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:1500])

# 3) Look at the recent Ledger events (deeper)
print()
print("=" * 60)
print("FRANTIC LEDGER (last 30 events)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_ledger","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    led = sc.get("ledger",{})
    events = led.get("events",[])
    print(f"  total events: {len(events)}")
    print()
    for e in events[:30]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:130]}")

# 4) Check AIA agentic market listing
print()
print("=" * 60)
print("AGENTIC.MARKET: check AIA")
print("=" * 60)
for q in ["razel369","aia","signal stream","rmalka06"]:
    s, d = fetch(f"https://api.agentic.market/v1/services/search?q={q}")
    print(f"  q={q}: status={s} type={type(d).__name__}")
    if isinstance(d, dict):
        svcs = d.get("services",[]) or d.get("data",[]) or d.get("items",[])
        print(f"    count: {len(svcs)}")
        for s2 in svcs[:2]:
            print(f"    - {s2.get('name','')[:60]} | {s2.get('url','')[:60]}")
    elif isinstance(d, list):
        print(f"    count: {len(d)}")
        for s2 in d[:2]:
            print(f"    - {s2.get('name','')[:60] if isinstance(s2, dict) else s2}")
