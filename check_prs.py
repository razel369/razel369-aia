#!/usr/bin/env python3
"""Check PRs + oath comment + try to improve #49."""
import json, urllib.request, urllib.error, os, subprocess

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

# 1) Check PRs via GitHub API
print("=" * 60)
print("MY PULL REQUESTS")
print("=" * 60)
for repo in ["razel369/AgentPipe","razel369/Open-Aeon","razel369/razel369-aia"]:
    s, d = fetch(f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=30",
                 headers={"Accept":"application/vnd.github+json"})
    if isinstance(d, list):
        print(f"  {repo}: {len(d)} PRs")
        for p in d[:10]:
            merged = p.get("merged_at") is not None
            print(f"    #{p['number']} {p['state']:>6} merged={merged}  {p['title'][:60]}  {p['html_url']}")

# 2) Check oath comment on issue
print()
print("=" * 60)
print("OATH COMMENT CHECK (auscaster/frantic-board#1)")
print("=" * 60)
s, d = fetch("https://api.github.com/repos/auscaster/frantic-board/issues/1/comments?per_page=20",
             headers={"Accept":"application/vnd.github+json"})
if isinstance(d, list):
    for c in d:
        body = c.get("body","")
        user = c.get("user",{}).get("login","?")
        print(f"  @{user} ({c.get('created_at','')[:19]}): {body[:200]}")

# 3) Check if I have any new comments on my issues (from Frantic bot)
print()
print("=" * 60)
print("COMMENTS ON MY REPOS (last 24h)")
print("=" * 60)
s, d = fetch("https://api.github.com/repos/razel369/razel369-aia/issues/comments?per_page=20",
             headers={"Accept":"application/vnd.github+json"})
if isinstance(d, list):
    for c in d[:10]:
        user = c.get("user",{}).get("login","?")
        body = c.get("body","")
        print(f"  @{user} ({c.get('created_at','')[:19]}): {body[:300]}")
