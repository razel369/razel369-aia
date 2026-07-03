#!/usr/bin/env python3
"""Check claimer + Frantic state after 30s."""
import json, urllib.request, urllib.error, time, os

def fetch(url, headers=None, method="GET", data=None, timeout=20):
    h = {"User-Agent":"Mozilla/5.0","Accept":"application/json, text/event-stream"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None: body = data.encode("utf-8")
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
    except Exception as e: return -1, str(e)

print("=" * 60)
print("CLAIMER LOG (after 30s)")
print("=" * 60)
log = r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.log"
if os.path.exists(log):
    with open(log) as f:
        print(f.read())
else:
    print("no log")

print()
print("=" * 60)
print("FRANTIC STATE NOW")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}")
    for ob in b.get("open_bounties",[]):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:60]}")
    feed = b.get("feed",[]) or []
    for e in feed[:3]:
        print(f"  {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:100]}")
