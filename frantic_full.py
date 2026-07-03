#!/usr/bin/env python3
"""Get full Frantic MCP manifest + look at runx repo structure."""
import json, urllib.request, urllib.error, re

def fetch(url, headers=None):
    h = {"User-Agent":"razel369-aia/1.0"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", errors="replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500], {}
    except Exception as e:
        return -1, str(e), {}

# 1) Full MCP manifest
print("=" * 60)
print("Full Frantic MCP manifest")
print("=" * 60)
s, body, _ = fetch("https://api.gofrantic.com/mcp.json", {"Accept":"application/json"})
print(f"size: {len(body)}")
print(body)

# 2) runx repo structure
print()
print("=" * 60)
print("runxhq/runx structure")
print("=" * 60)
def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]
    except Exception as e:
        return -1, str(e)

s, d = gh("/repos/runxhq/runx")
if s == 200:
    print(f"desc: {d.get('description','')[:300]}")
    print(f"★ {d.get('stargazers_count')}, fork: {d.get('forks_count')}")
    print(f"default_branch: {d.get('default_branch')}")
    print(f"created: {d.get('created_at')}")
s, d = gh("/repos/runxhq/runx/contents/")
if s == 200:
    for it in d:
        print(f"  {it.get('type','blob'):4} {it.get('name')}  ({it.get('size',0)} bytes)")
s, d = gh("/repos/runxhq/runx/git/trees/main?recursive=1")
if s == 200:
    tree = d.get("tree", [])
    print(f"\nFull tree ({len(tree)} entries):")
    for it in tree[:60]:
        print(f"  {it.get('type','blob'):4} {it.get('path')}  ({it.get('size',0)}b)")
    if len(tree) > 60:
        print(f"  ... +{len(tree)-60} more")

# 3) runx README
print()
print("=" * 60)
print("runx README")
print("=" * 60)
s, body, _ = fetch("https://raw.githubusercontent.com/runxhq/runx/main/README.md")
if s == 200:
    print(body[:5000])
