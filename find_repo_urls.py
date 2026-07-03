#!/usr/bin/env python3
"""Find actual repos + try direct issue URL."""
import json, urllib.request, urllib.error, urllib.parse

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

# 1) Find the repo behind lux #67
print("=" * 60)
print("Find lux issue #67 repo")
print("=" * 60)
s, d = gh("/search/issues?q=repo:lux/lux+67+is:issue")
if s == 200:
    for it in d.get("items",[])[:5]:
        print(f"  repo_url: {it.get('repository_url','')}")
        print(f"  html_url: {it.get('html_url','')}")
        print(f"  title: {it.get('title','')[:80]}")

# 2) Search for "lux" + Telegram + bounty in any org
print()
print("=" * 60)
print("Search for Telegram Analytics bounty")
print("=" * 60)
s, d = gh("/search/issues?q=%22Telegram+Analytics%22+%22%241%2C200%22&per_page=5")
if s == 200:
    for it in d.get("items",[]):
        print(f"  repo: {it.get('repository_url','').split('/')[-1]}")
        print(f"  html: {it.get('html_url','')}")
        print(f"  title: {it.get('title','')[:80]}")

# 3) Find what orgs have Algora bounties
print()
print("=" * 60)
print("Search issues with Algora and USDC")
print("=" * 60)
queries = [
    '"$1200" OR "$1,200" label:bounty is:open',
    '"$1800" OR "$1,800" label:bounty is:open',
    '"$2500" OR "$2,500" label:bounty is:open',
    'in:title "Telegram" is:issue',
    '"PayPal Sandbox" AND "USDT" is:issue',
]
for q in queries:
    s, d = gh(f"/search/issues?q={urllib.parse.quote(q)}&per_page=5")
    if s == 200:
        items = d.get("items", [])
        if items:
            print(f"  q={q!r}: {len(items)}")
            for it in items[:3]:
                repo = it.get("repository_url","").replace("https://api.github.com/repos/","")
                print(f"    {repo} #{it.get('number')} {it.get('title')[:60]}")

# 4) Look at Algora's own org to find all bounties
print()
print("=" * 60)
print("Algora's own bounties via search")
print("=" * 60)
s, d = gh("/search/issues?q=console.algora.io+OR+algora.io+is:open&per_page=10")
if s == 200:
    for it in d.get("items",[]):
        repo = it.get("repository_url","").replace("https://api.github.com/repos/","")
        body = (it.get("body","") or "")[:200]
        print(f"  {repo} #{it.get('number')} {it.get('title')[:60]}")
        print(f"    body: {body}")

# 5) Algora API with different path
print()
print("=" * 60)
print("Algora API paths")
print("=" * 60)
for path in [
    "/api/v1/bounties?status=open",
    "/api/bounties?status=open&per_page=30",
    "/api/bounties",
    "/api/v1/orgs/dwebagents/bounties",
    "/api/orgs/dwebagents/bounties?status=open",
]:
    try:
        req = urllib.request.Request("https://console.algora.io" + path,
            headers={"User-Agent":"razel369-aia/1.0","Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            print(f"  {r.status} {len(body)}b  {path}")
    except urllib.error.HTTPError as e:
        print(f"  {e.code}  {path}")
    except Exception as e:
        print(f"  err: {e}  {path}")
