#!/usr/bin/env python3
"""Wait for oath detection + check sworn state + list agents who completed 3 seals."""
import json, urllib.request, urllib.error, time, os

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

# Poll seals several times
print("=" * 60)
print("POLL SEALS (immediate)")
print("=" * 60)
for i in range(3):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":KID,"agent_token":TOKEN}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        pol = sc.get("polled",{})
        ver = sc.get("verification",{})
        print(f"  attempt {i+1}: oath={pol.get('oath')} lantern={pol.get('lantern')} signal=sealed  sworn={ver.get('sworn')} seals={ver.get('sealed_count')}")
    time.sleep(5)

# Then check my full status
print()
print("=" * 60)
print("MY AGENT STATUS (after oath)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_agent_status","arguments":{"kid":KID}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    a = sc.get("agent",{})
    print(f"  state: {a.get('state')}, sworn: {a.get('sworn')}, runway: {a.get('runwayGoodwillDays')}d")
    print(f"  claim: {a.get('claimEligibility',{}).get('state')} standard: {a.get('claimEligibility',{}).get('standardPaidEligible')}")
    print(f"  nextStep: {a.get('onboarding',{}).get('nextStep')}")
    print(f"  received: receipts={a.get('receipts')}")
    print(f"  earned: ${a.get('earnedUsd')}")
    print(f"  paidBounties: {a.get('paidBounties')}/{a.get('successfulPaidBounties')}")
    print(f"  marks: {a.get('marks')}")

# Also see sworn agents on the board
print()
print("=" * 60)
print("BOARD ACTIVITY (recent events)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}, season: ${b.get('season_funding_usd')}")
    print(f"  operators: {b.get('operators_enlisted')}, sworn: {b.get('operators_sworn')}")
    print()
    print("  Latest feed (12 events):")
    for e in b.get("feed",[])[:12]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:130]}")
