#!/usr/bin/env python3
"""Get #11 details + my full agent state + check for new paid bounties."""
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

# 1) Get #11 details
print("=" * 60)
print("FRANTIC #11 (just got delivered)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_bounty","arguments":{"bounty_id":11}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("bounty",{})
    print(f"  #{b.get('number')} ${b.get('price_usd')} {b.get('title','')}")
    print(f"  state: {b.get('state')}")
    print(f"  claim_window: {b.get('claim_window_seconds')}s")
    print(f"  body: {(b.get('body_md') or b.get('body',''))[:600]}")
    print(f"  deliverables_required: {b.get('deliverables_required')}")
    print(f"  reviewer_mode: {b.get('reviewer_mode')}")
    print()
    print(f"  Full bounty keys: {list(b.keys())}")

# 2) My agent status — look at all fields
print()
print("=" * 60)
print("MY AGENT (raw fields)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_agent_status","arguments":{"kid":"agent-b62bf6"}}})
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:3000])
