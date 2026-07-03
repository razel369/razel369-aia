#!/usr/bin/env python3
"""Check high-value Frantic bounties (open) + speed-claim setup + look for more auto-pay repos."""
import json, urllib.request, urllib.error, subprocess, time, os

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

# 1) Check high-value Frantic bounties
print("=" * 60)
print("FRANTIC HIGH-VALUE BOUNTIES (check if any opened)")
print("=" * 60)
high_value = [1, 2, 3, 4, 5, 6, 7, 8, 17, 18, 19, 20, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 46, 47, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
open_high = []
for bid in high_value:
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if isinstance(b, dict):
            ps = b.get("postingStatus","?")
            ws = b.get("workStatus","?")
            price = b.get("priceUsd") or 0
            cp = b.get("claimProgress",{})
            avail = cp.get("available", 0)
            cap = cp.get("capacity", 0)
            if avail > 0 and price > 0:
                open_high.append((bid, price, avail, b.get("title","")))
                print(f"  !!! OPEN: #{bid} ${price} avail={avail}/{cap} {b.get('title','')[:70]}")
    time.sleep(0.15)
print(f"\n  TOTAL OPEN HIGH-VALUE: {len(open_high)}")

# 2) Check dwebagents org for other auto-pay repos
print()
print("=" * 60)
print("DWEBAGENTS ORG REPOS")
print("=" * 60)
s, d = fetch("https://api.github.com/orgs/dwebagents/repos?per_page=30&sort=updated",
             headers={"Accept":"application/vnd.github+json"})
if isinstance(d, list):
    for r in d[:20]:
        print(f"  {r.get('full_name')} - {r.get('description','')[:80] if r.get('description') else '(no desc)'}")

# 3) Check if my Open-Aeon PR is getting any attention
print()
print("=" * 60)
print("OPEN-AEON PR #2 — recent activity")
print("=" * 60)
comments = None
r = subprocess.run(["gh","api","repos/jessedaustin93/Open-Aeon/issues/2/comments?per_page=10"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: comments = json.loads(r.stdout)
    except: pass
if isinstance(comments, list):
    for c in comments[:5]:
        print(f"  @{c.get('user',{}).get('login','?')}: {c.get('body','')[:200]}")

# 4) Check AgentPipe for any auto-merge bot activity
print()
print()
print("=" * 60)
print("AGENTPIPE PR #1941 — recent activity")
print("=" * 60)
r = subprocess.run(["gh","api","repos/dwebagents/AgentPipe/issues/1941/comments?per_page=10"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: comments = json.loads(r.stdout)
    except: pass
if isinstance(comments, list):
    for c in comments[:5]:
        print(f"  @{c.get('user',{}).get('login','?')}: {c.get('body','')[:200]}")

# 5) Look for ANY new high-value bounty in past 7 days
print()
print("=" * 60)
print("RECENT PAID FRANTIC BOUNTIES (top 10)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_ledger","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    led = sc.get("ledger",{})
    # Look for "GOODWILL" or "DELIVERED" or "PAID" with $
    events = led.get("events",[])
    print(f"  total events in ledger: {len(events)}")
    print()
    print("  All events (last 20):")
    for e in events[:20]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:130]}")
