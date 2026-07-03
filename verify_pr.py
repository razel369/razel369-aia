#!/usr/bin/env python3
"""Verify AgentPipe PR #1941 now shows proper diff + check for AIA improvements + Frantic poll."""
import json, urllib.request, urllib.error, subprocess, time

def gh(path):
    try:
        r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            try: return json.loads(r.stdout)
            except: return r.stdout
        return None
    except: return None

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

# 1) Verify PR #1941 now has proper diff
print("=" * 60)
print("AGENTPIPE PR #1941 — verify diff is now text")
print("=" * 60)
pr = gh("repos/dwebagents/AgentPipe/pulls/1941")
if pr:
    print(f"  additions: {pr.get('additions')}, deletions: {pr.get('deletions')}")
    print(f"  changed_files: {pr.get('changed_files')}")

files = gh("repos/dwebagents/AgentPipe/pulls/1941/files")
if isinstance(files, list):
    for f in files:
        print(f"  {f.get('status')} {f.get('filename')} +{f.get('additions')} -{f.get('deletions')}")
        patch = f.get('patch','')
        if patch:
            print(f"    patch[:300]: {patch[:300]}")

# 2) Get the actual file content as GitHub sees it
print()
print("=" * 60)
print("FILE CONTENT (from upstream)")
print("=" * 60)
s, d = fetch("https://raw.githubusercontent.com/dwebagents/AgentPipe/aa70d46cb0689e6b2c3a431bc729a79bbe8e8bf0/contributors.html")
if isinstance(d, str):
    print(f"  size: {len(d)}")
    import re
    cnt = len(re.findall(r"71", d))
    print(f"  71 count: {cnt}")
    print(f"  has goose: {'goose' in d.lower()}")
    print(f"  has golden egg: {'golden egg' in d.lower()}")
    print(f"  has easter egg: {'easter' in d.lower()}")
    print(f"  has factory: {'factor' in d.lower()}")
    print(f"  first 500: {d[:500]}")

# 3) Quick Frantic poll - any new bounties?
print()
print("=" * 60)
print("FRANTIC: quick poll for new paid bounties")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}, season: ${b.get('season_funding_usd')}")
    for ob in b.get("open_bounties",[]):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:60]}")
    # Last 3 events
    for e in b.get("feed",[])[:3]:
        print(f"  {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:100]}")
