#!/usr/bin/env python3
"""Look up Frantic, #1909 (doohickey), and #1887 (hiring)."""
import json, urllib.request, urllib.error, re

def gh(method, path, data=None):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        data=json.dumps(data).encode("utf-8") if data else None,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

# 1) Look at #1909 with comments
print("=" * 60)
print("#1909 Doohickey Interface (full issue + comments)")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1909")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"comments: {d.get('comments')}")
    print(f"body:\n{d.get('body','')}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1909/comments?per_page=20")
if s == 200:
    for c in d:
        print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:600]}")
        print("  ---")

# 2) #1909 mentioned PRs
print()
print("=" * 60)
print("PRs linked to #1909")
print("=" * 60)
s, d = gh("GET", "/search/issues?q=repo:dwebagents/AgentPipe+1909+is:pr")
if s == 200:
    for it in d.get("items",[])[:5]:
        print(f"  #{it.get('number')} {it.get('state')}: {it.get('title')[:80]}")

# 3) #1887
print()
print("=" * 60)
print("#1887 Hiring system (full)")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1887")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"body:\n{d.get('body','')}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1887/comments?per_page=20")
if s == 200:
    for c in d:
        print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:600]}")
        print("  ---")

# 4) Find doohickey/interface files
print()
print("=" * 60)
print("Doohickey interface: list src/ structure")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/contents/src")
if s == 200:
    for it in d:
        print(f"  {it.get('type'):4} {it.get('name')}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/git/trees/main?recursive=1")
if s == 200:
    tree = d.get("tree", [])
    # Find files related to doohickey, interface, gizmo
    for it in tree:
        path = it.get("path","")
        if any(kw in path.lower() for kw in ["doohickey","interface","gizmo","whatsit","plugin"]):
            print(f"  {it.get('type','blob'):4} {path}")
    # Also show top-level
    print()
    print("Top-level files:")
    for it in tree:
        path = it.get("path","")
        if "/" not in path:
            print(f"  {it.get('type','blob'):4} {path}  ({it.get('size',0)} bytes)")

# 5) Frantic lookup
print()
print("=" * 60)
print("Frantic (gofrantic.com)")
print("=" * 60)
for url in ["https://gofrantic.com", "https://gofrantic.com/bounties", "https://gofrantic.com/api/bounties", "https://gofrantic.com/.well-known/x402"]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8", errors="replace")
            text = re.sub(r"<[^>]+>"," ", body)
            text = re.sub(r"\s+", " ", text)
            print(f"  {url} → {r.status} (size {len(body)})")
            print(f"    {text[:300]}")
    except urllib.error.HTTPError as e:
        print(f"  {url} → {e.code}")
    except Exception as e:
        print(f"  {url} → err: {e}")

# 6) Search GitHub for Frantic-related repos
print()
print("=" * 60)
print("GitHub: Frantic-related repos")
print("=" * 60)
import urllib.parse
for q in ["gofrantic", "frantic-bounties", "frantic-eth"]:
    s, d = gh("GET", f"/search/repositories?q={urllib.parse.quote(q)}&per_page=5")
    if s == 200:
        for it in d.get("items",[]):
            print(f"  ★{it.get('stargazers_count',0):>4}  {it.get('full_name')}: {it.get('description','')[:80]}")
