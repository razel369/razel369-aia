#!/usr/bin/env python3
"""Fetch Frantic API + bounties + check #1926 doohickey PR."""
import json, urllib.request, urllib.error, re, urllib.parse

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

def fetch(url, headers=None):
    h = {"User-Agent":"razel369-aia/1.0"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return -1, str(e)

# 1) Check #1926 (doohickey PR) status - was already opened
print("=" * 60)
print("#1926 doohickey PR status")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/pulls/1926")
if s == 200:
    print(f"state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"title: {d.get('title')}")
    print(f"user: {d.get('user',{}).get('login')}")
    print(f"head: {d.get('head',{}).get('ref')}  base: {d.get('base',{}).get('ref')}")
    print(f"files: {len(d.get('files',[]))}")
    for f in d.get("files",[]):
        print(f"  {f.get('filename')}: +{f.get('additions')}/-{f.get('deletions')}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1926/comments?per_page=10")
if s == 200:
    for c in d:
        print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("  ---")

# 2) Frantic homepage - what bounties look like
print()
print("=" * 60)
print("Frantic homepage structure")
print("=" * 60)
s, body = fetch("https://gofrantic.com")
if s == 200:
    # Find JSON data, bounty ids, link patterns
    print(f"size: {len(body)} bytes")
    # Look for Frantic IDs (8 hex)
    for m in re.finditer(r'/r/([a-f0-9]+)', body)[:5] if False else []:
        pass
    ids = list(set(re.findall(r'/r/([a-f0-9]{8,})', body)))[:10]
    print(f"Frantic delivery IDs: {ids}")
    # Find link patterns
    for kw in ["/bounties", "/bounty", "/board", "/agent", "/api", "payout", "deliver"]:
        matches = re.findall(r'href="([^"]*' + kw + r'[^"]*)"', body, re.IGNORECASE)
        for m in matches[:3]:
            print(f"  href: {m}")
    # Find a-b-c bounty counts
    text = re.sub(r"<[^>]+>"," ",body)
    text = re.sub(r"\s+"," ",text)
    print()
    print("First 2000 chars:", text[:2000])

# 3) Frantic auscaster/frantic-board repo
print()
print("=" * 60)
print("auscaster/frantic-board")
print("=" * 60)
s, d = gh("GET", "/repos/auscaster/frantic-board")
if s == 200:
    print(f"desc: {d.get('description','')[:200]}")
    print(f"★ {d.get('stargazers_count')}, default_branch: {d.get('default_branch')}")
s, d = gh("GET", "/repos/auscaster/frantic-board/contents/")
if s == 200:
    for it in d[:15]:
        print(f"  {it.get('type','blob'):4} {it.get('name')}  ({it.get('size',0)} bytes)")

# 4) Frantic API discovery
print()
print("=" * 60)
print("Frantic API attempts")
print("=" * 60)
for url in [
    "https://gofrantic.com/api/v1/bounties",
    "https://gofrantic.com/api/bounties",
    "https://api.gofrantic.com/bounties",
    "https://gofrantic.com/api/agents",
    "https://gofrantic.com/agents",
    "https://gofrantic.com/bounty",
    "https://gofrantic.com/api/board",
    "https://gofrantic.com/.well-known/x402",
]:
    s, body = fetch(url, {"Accept":"application/json"})
    print(f"  {s} {len(body):>6}b  {url}")

# 5) Try going directly to a delivery ID
print()
print("=" * 60)
print("Sample Frantic delivery page")
print("=" * 60)
s, body = fetch("https://gofrantic.com/r/254f46ec0092")
if s == 200:
    text = re.sub(r"<[^>]+>"," ",body)
    text = re.sub(r"\s+"," ",text)
    print("First 1500 chars:", text[:1500])

# 6) Search for other Frantic refs in agent repos
print()
print("=" * 60)
print("Frantic 'gofrantic.com' mentions in agent repos")
print("=" * 60)
s, d = gh("GET", "/search/code?q=%22gofrantic.com%22+agent&per_page=10")
if s == 200:
    for it in d.get("items",[])[:10]:
        print(f"  {it.get('repository',{}).get('full_name')}: {it.get('path')}")
