#!/usr/bin/env python3
"""Discover ALL Frantic bounties + check what '3 seals' means + claim eligibility."""
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

# 1) Try reading the ledger for ALL bounties
print("=" * 60)
print("FRANTIC LEDGER (all bounties)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_ledger","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    print(f"  keys: {list(sc.keys())[:30]}")
    for k, v in sc.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
            for item in v[:5]:
                print(f"    {json.dumps(item)[:200]}")
        elif isinstance(v, dict):
            print(f"  {k}: {json.dumps(v)[:200]}")
        else:
            print(f"  {k}: {v}")

# 2) Try specific bounty IDs (1-20)
print()
print("=" * 60)
print("FRANTIC BOUNTIES 1-20")
print("=" * 60)
for bid in range(1, 21):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"bounty_id":bid}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if b and b.get("title"):
            print(f"  #{bid} ${b.get('price_usd','?')} state={b.get('state','?')} title={b.get('title','')[:80]}")
            print(f"        mode={b.get('reviewer_mode','?')} window={b.get('claim_window_seconds','?')}s")
            print(f"        body: {(b.get('body_md') or b.get('body') or '')[:300]}")

# 3) What does 'lantern' next-step mean? Check my receipts
print()
print("=" * 60)
print("MY RECEIPTS / SEALS")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.poll_seals","arguments":{"kid":"agent-b62bf6"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    print(json.dumps(sc, indent=2)[:3000])
