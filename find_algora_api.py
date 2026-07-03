#!/usr/bin/env python3
"""Find Algora org/bounty API via page links + curl emulation."""
import urllib.request, urllib.error, re, base64, json

def fetch(url, headers=None, method="GET", data=None, timeout=20):
    h = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","Accept":"*/*"}
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

# 1) Look at console.algora.io main page for org links
print("=" * 60)
print("console.algora.io main page - find org links")
print("=" * 60)
s, d = fetch("https://console.algora.io/")
if s == 200 and isinstance(d, str):
    # Find org links
    orgs = set()
    for m in re.finditer(r'href="(/o/([a-zA-Z0-9_-]+)[^"]*)"', d):
        orgs.add((m.group(2), m.group(1)))
    for org, path in sorted(orgs)[:20]:
        print(f"  {org}: {path}")

# 2) Try org pages
print()
print("=" * 60)
print("Try /o/<org> pages")
print("=" * 60)
for org in ["coderabbit","firecrawl","containerd","comfy","cloudflare"]:
    for path in [f"/o/{org}", f"/o/{org}/bounties", f"/bounties?org={org}", f"/o/{org}.json"]:
        s, d = fetch(f"https://console.algora.io{path}", timeout=10)
        if s == 200 and isinstance(d, str) and "bount" in d.lower():
            print(f"  {s} {len(d)}b  {path}")
            # Find JSON data in page
            for m in re.finditer(r'\{[^{}]*bount[^{}]*\}', d):
                print(f"    JSON: {m.group(0)[:200]}")

# 3) Try the API at api.algora.io with proper auth headers
print()
print("=" * 60)
print("api.algora.io with proper headers")
print("=" * 60)
for url in [
    "https://api.algora.io/bounties?status=open",
    "https://api.algora.io/bounties?status=open&per_page=30",
    "https://api.algora.io/v1/bounties?status=open",
    "https://api.algora.io/api/bounties?status=open",
    "https://api.algora.io/public/bounties?status=open",
    "https://api.algora.io/api/v1/public/bounties?status=open",
    "https://api.algora.io/api/v2/bounties?status=open",
]:
    s, d = fetch(url, headers={"Accept":"application/json","User-Agent":"curl/7.88.1","Origin":"https://console.algora.io"}, timeout=10)
    if s == 200:
        if isinstance(d, dict):
            print(f"  {s} keys={list(d.keys())[:5]}  {url}")
        elif isinstance(d, list):
            print(f"  {s} {len(d)} items  {url}")
            for b in d[:2]:
                print(f"    {b}")
    elif s != 404 and s != 406 and s != 429:
        print(f"  {s}  {url}")
