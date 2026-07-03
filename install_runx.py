#!/usr/bin/env python3
"""Start FAST Frantic monitor (5s) + install runx + prep Show HN submit."""
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

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

# 1) Try install runx
print("=" * 60)
print("INSTALL RUNX")
print("=" * 60)
for cmd in ["pip install runx --quiet", "pip install runx-cli --quiet", "pip install runx-cli", "npm install -g runx 2>&1 | Select-Object -First 5"]:
    rc, out, err = run(cmd, timeout=60)
    print(f"  $ {cmd[:40]}")
    print(f"    rc={rc}, out={out[:200].strip()}, err={err[:200].strip()}")

# 2) Get more Frantic bounty info on #11 (the one that was claimed)
print()
print("=" * 60)
print("FRANTIC #11 (was claimed, want to know the work pattern)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_bounty","arguments":{"id":"11"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
    if isinstance(b, dict):
        print(f"  title: {b.get('title')}")
        print(f"  price: ${b.get('priceUsd')}")
        print(f"  workStatus: {b.get('workStatus')}")
        print(f"  ps: {b.get('postingStatus')}")
        print(f"  acceptance criteria:")
        for a in b.get("criteria",{}).get("acceptance",[]):
            print(f"    - {a[:200]}")
        print(f"  artifacts: {b.get('criteria',{}).get('artifacts',[])}")
        # Look at events
        print()
        print("  events (last 8):")
        for e in b.get("events",[])[-8:]:
            print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:120]}")

# 3) Get info on a simpler paid bounty #15 (Break the front door)
print()
print("=" * 60)
print("FRANTIC #15 (simpler entry)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_bounty","arguments":{"id":"15"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
    if isinstance(b, dict):
        print(f"  title: {b.get('title')}")
        print(f"  price: ${b.get('priceUsd')}")
        print(f"  desc: {b.get('description','')[:1000]}")
        print()
        print(f"  acceptance criteria:")
        for a in b.get("criteria",{}).get("acceptance",[]):
            print(f"    - {a[:200]}")
        print(f"  artifacts: {b.get('criteria',{}).get('artifacts',[])}")

# 4) Look at Frantic runx skill bounty #19 (structured extraction) — what work is needed
print()
print("=" * 60)
print("FRANTIC #19 (structured extraction)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_bounty","arguments":{"id":"19"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
    if isinstance(b, dict):
        print(f"  title: {b.get('title')}")
        print(f"  price: ${b.get('priceUsd')}")
        print(f"  desc: {b.get('description','')[:1500]}")
