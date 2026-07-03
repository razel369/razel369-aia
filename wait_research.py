#!/usr/bin/env python3
"""While rate-limited: check Frantic, look for direct Algora endpoint, update dashboard."""
import json, urllib.request, urllib.error, time, subprocess, base64

def fetch(url, headers=None, method="GET", data=None, timeout=30):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
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

# 1) Frantic board - any new bounties?
print("=" * 60)
print("Frantic board")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_board","arguments":{}}
})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}, operators: {b.get('operators_enlisted')}")
    for ob in b.get("open_bounties", []):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title')[:60]}")
    # Recent events
    print("\n  Recent events:")
    for e in b.get("feed",[])[:10]:
        print(f"    {e.get('at','')[:19]} {e.get('kind'):>10}  {e.get('text','')[:120]}")

# 2) Look at AgentPipe PR #1941 status
print()
print("=" * 60)
print("AgentPipe PR #1941 status")
print("=" * 60)
s, d = fetch("https://api.github.com/repos/dwebagents/AgentPipe/pulls/1941")
if s == 200:
    print(f"  state: {d.get('state')}, merged: {d.get('merged')}, mergeable: {d.get('mergeable')}")
    print(f"  title: {d.get('title')}")
    print(f"  comments: {d.get('comments')}, review_comments: {d.get('review_comments')}")
s, d = fetch("https://api.github.com/repos/dwebagents/AgentPipe/issues/1941/comments?per_page=20")
if s == 200:
    for c in d:
        print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("  ---")

# 3) Open-Aeon PR #2
print()
print("=" * 60)
print("Open-Aeon PR #2")
print("=" * 60)
s, d = fetch("https://api.github.com/repos/jessedaustin93/Open-Aeon/pulls/2")
if s == 200:
    print(f"  state: {d.get('state')}, merged: {d.get('merged')}")
else:
    print(f"  PR fetch: {s} {str(d)[:200]}")
s, d = fetch("https://api.github.com/repos/jessedaustin93/Open-Aeon/issues/2/comments?per_page=10")
if s == 200:
    for c in d:
        print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("  ---")

# 4) Look for the actual Algora API
print()
print("=" * 60)
print("Algora - try discovery")
print("=" * 60)
# Algora's app is at console.algora.io - check the JS bundle
for url in [
    "https://console.algora.io/",
    "https://www.algora.io/",
    "https://api.algora.io",
]:
    s, body = fetch(url, timeout=10)
    print(f"  {s}  {url}")
    if s == 200:
        text = body if isinstance(body, str) else json.dumps(body)
        # Find any API endpoints
        for m in re.finditer(r"https?://[^\"'<>\\s]+", text):
            u = m.group(0)
            if "api" in u or "bounties" in u:
                print(f"    API ref: {u[:120]}")
                break
import re
