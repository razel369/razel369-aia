#!/usr/bin/env python3
"""Continued parallel work."""
import json, urllib.request, urllib.error, re, urllib.parse

def fetch(url, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(text)
            except:
                return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except:
            return e.code, text
    except Exception as e:
        return -1, str(e)

def gh(method, path, data=None, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request("https://api.github.com" + path, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(text)
            except:
                return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except:
            return e.code, text
    except Exception as e:
        return -1, str(e)

# 1) Open-Aeon status
print("=" * 60)
print("Open-Aeon PR #2 + Issue #1")
print("=" * 60)
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/pulls/2")
print(f"PR #2: status={s}")
if s == 200:
    print(f"  state: {d.get('state')}, merged: {d.get('merged')}, mergeable: {d.get('mergeable')}")
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/issues/2/comments?per_page=10")
print(f"  comments: {s} {len(d) if isinstance(d,list) else 'err'}")
if isinstance(d, list):
    for c in d:
        print(f"    {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("    ---")
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/issues/1?per_page=10")
if s == 200:
    print(f"\nIssue #1: {d.get('title')}")
    print(f"  state: {d.get('state')}, body: {d.get('body','')[:500]}")
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/issues/1/comments?per_page=10")
if isinstance(d, list):
    for c in d:
        print(f"    {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("    ---")

# 2) Check if there are even more direct agentic.market URLs
print()
print("=" * 60)
print("agentic.market - search AIA")
print("=" * 60)
s, d = fetch("https://api.agentic.market/v1/services/search?q=aia")
if s == 200:
    services = d.get("services", [])
    print(f"aia search: {len(services)} results")
    for sv in services[:3]:
        print(f"  {sv.get('name')} (${sv.get('priceSummary',{}).get('minAmount','?')}/call)")
s, d = fetch("https://api.agentic.market/v1/services/search?q=razel369")
if s == 200:
    print(f"razel369 search: {len(d.get('services',[]))} results")
s, d = fetch("https://api.agentic.market/v1/services/search?q=insight+agent")
if s == 200:
    print(f"insight agent search: {len(d.get('services',[]))} results")
    for sv in d.get("services",[])[:3]:
        print(f"  {sv.get('name')}: {sv.get('description','')[:80]}")

# 3) Try posting via different content-type
print()
print("=" * 60)
print("Try POST with different formats")
print("=" * 60)
endpoints = [
    "https://api.agentic.market/v1/services",
    "https://api.agentic.market/services",
    "https://agentic.market/api/v1/services",
]
aia_payload = {"id":"aia-x402","name":"AIA","domain":"aia-x402.rmalka06.workers.dev","networks":["eip155:8453"]}
for url in endpoints:
    for ct in ["application/json","application/x-www-form-urlencoded"]:
        try:
            if ct == "application/json":
                data = json.dumps(aia_payload).encode("utf-8")
            else:
                data = urllib.parse.urlencode(aia_payload).encode("utf-8")
            req = urllib.request.Request(url, method="POST", data=data,
                headers={"Content-Type":ct,"User-Agent":"razel369-aia/1.0","Accept":"application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                print(f"  {ct[:25]:25} POST {url} → {r.status}")
        except urllib.error.HTTPError as e:
            print(f"  {ct[:25]:25} POST {url} → {e.code}")
        except Exception as e:
            print(f"  {ct[:25]:25} POST {url} → err: {e}")

# 4) Find more bounties
print()
print("=" * 60)
print("More bounty sources (Opire repos, GrantFox, XPRize)")
print("=" * 60)
queries = [
    "org:claude-builders-bounty",
    "org:Markp1598M",
    "org:walletbeat",
    "org:rustchain-bounties",
    "org:xevrion-v2",
    "org:cocohub-mobileapp"
]
for q in queries:
    s, d = gh("GET", f"/search/issues?q={urllib.parse.quote(q)}+is:issue&per_page=5")
    if s == 200:
        items = d.get("items", [])
        print(f"  {q}: {len(items)} issues")
        for it in items[:3]:
            print(f"    #{it.get('number')} {it.get('title')[:80]}")

# 5) Also search for direct USDC bounty listings
print()
print("=" * 60)
print("Algora direct USDC bounties")
print("=" * 60)
s, d = gh("GET", "/search/issues?q=algora+usdc+bounty+is:open&per_page=10")
if s == 200:
    for it in d.get("items",[])[:5]:
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} {it.get('repository_url','').split('/')[-1]} [{','.join(labels[:3])}] {it.get('title')[:60]}")
