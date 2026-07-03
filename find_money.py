#!/usr/bin/env python3
"""Look at recent Frantic paid bounty completions + find auto-pay GitHub programs + high-value actions."""
import json, urllib.request, urllib.error, re, subprocess, time

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

def gh(path):
    try:
        r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            try: return json.loads(r.stdout)
            except: return r.stdout
        return None
    except: return None

# 1) Recent Frantic PAID completions (last 20 events with PAID kind)
print("=" * 60)
print("FRANTIC: recent PAID events (last 50 events)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_ledger","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    led = sc.get("ledger",{})
    events = led.get("events",[])
    # Filter for PAID events
    paid = [e for e in events if e.get("kind") == "PAID" or "$" in e.get("text","")]
    print(f"  total events: {len(events)}, paid-related: {len(paid)}")
    print()
    for e in paid[:20]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:130]}")

# 2) Find Frantic bounties that have been FUNDED but not yet started (look for FUNDED events)
print()
print("=" * 60)
print("FRANTIC: recent FUNDED events (look for new paid)")
print("=" * 60)
if isinstance(d, dict):
    funded = [e for e in events if e.get("kind") == "FUNDED"]
    print(f"  funded events: {len(funded)}")
    for e in funded[:20]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:130]}")

# 3) Search GitHub for auto-pay programs
print()
print("=" * 60)
print("GITHUB: search for auto-pay programs")
print("=" * 60)
queries = [
    "bounty auto pay merge",
    "paid on merge github bot USDC",
    "first PR merged USDC",
    "contributor payout bot",
    "github bot pays contributors",
]
for q in queries:
    s, d = fetch(f"https://api.github.com/search/repositories?q={urllib.request.quote(q)}&sort=updated&per_page=5",
                 headers={"Accept":"application/vnd.github+json"})
    if isinstance(d, dict):
        items = d.get("items",[])
        if items:
            print(f"  q={q}: {d.get('total_count')} results")
            for r in items[:3]:
                print(f"    {r.get('full_name')}: {r.get('description','')[:80] if r.get('description') else ''}")

# 4) Look for GitHub Actions-based auto-pay
print()
print("=" * 60)
print("GITHUB: search for paid-auto-bot")
print("=" * 60)
queries = [
    "polar pay bot",
    "github sponsors bot",
    "tip jar github bot",
    "usdc auto pay issue",
]
for q in queries:
    s, d = fetch(f"https://api.github.com/search/repositories?q={urllib.request.quote(q)}&sort=updated&per_page=3",
                 headers={"Accept":"application/vnd.github+json"})
    if isinstance(d, dict):
        items = d.get("items",[])
        if items:
            print(f"  q={q}: {d.get('total_count')} results")
            for r in items[:2]:
                print(f"    {r.get('full_name')}: {r.get('description','')[:80] if r.get('description') else ''}")
