#!/usr/bin/env python3
"""EXPLORE x402scan.com — the main x402 registry with 1483 services."""
import json, urllib.request, urllib.error, re, time

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

# 1) Get the main page
print("=" * 60)
print("x402scan.com MAIN PAGE")
print("=" * 60)
s, d = fetch("https://x402scan.com")
if isinstance(d, str):
    # Find API endpoints
    for m in re.finditer(r'(/api/[a-zA-Z0-9_/-]+|/v\d+/[a-zA-Z0-9_/-]+)', d):
        print(f"  {m.group(0)}")
    # Find where to submit
    for kw in ["submit","add service","register","new service","how to list","add your"]:
        idx = d.lower().find(kw)
        if idx > 0:
            print(f"  '{kw}': ...{d[max(0,idx-30):idx+200]}...")

# 2) Try common API endpoints
print()
print("=" * 60)
print("x402scan.com API")
print("=" * 60)
endpoints = [
    "https://x402scan.com/api/services",
    "https://x402scan.com/api/v1/services",
    "https://api.x402scan.com/services",
    "https://x402scan.com/api",
    "https://x402scan.com/api/listings",
    "https://x402scan.com/api/resources",
    "https://www.x402scan.com/api/services",
]
for u in endpoints:
    s, d = fetch(u, headers={"Accept":"application/json"})
    if s == 200:
        if isinstance(d, dict):
            print(f"  {s} {u}  keys: {list(d.keys())[:5]}")
        elif isinstance(d, list):
            print(f"  {s} {u}  list: {len(d)}")
        else:
            print(f"  {s} {u}  ({len(d)}b)")
    else:
        print(f"  {s} {u}")

# 3) Find assets
print()
print("=" * 60)
print("x402scan.com ASSETS (JS)")
print("=" * 60)
s, d = fetch("https://x402scan.com")
if isinstance(d, str):
    js_urls = set()
    for m in re.finditer(r'src="(/[a-zA-Z0-9_./-]+\.js[^"]*)"', d):
        js_urls.add(m.group(1))
    for m in re.finditer(r'src="(https://[^"]*x402[^"]*\.js[^"]*)"', d):
        js_urls.add(m.group(1))
    for m in re.finditer(r'"(/[a-zA-Z0-9_./-]+\.js[^"]*)"', d):
        js_urls.add(m.group(1))
    for u in list(js_urls)[:10]:
        print(f"  {u[:100]}")

# 4) Find submit endpoint in HTML
print()
print("=" * 60)
print("x402scan.com HTML STRUCTURE")
print("=" * 60)
s, d = fetch("https://x402scan.com")
if isinstance(d, str):
    # Look for form action
    for m in re.finditer(r'<form[^>]+action="([^"]+)"', d):
        print(f"  form action: {m.group(1)}")
    for m in re.finditer(r'data-([a-zA-Z-]+)="([^"]+)"', d):
        if 'submit' in m.group(1).lower() or 'service' in m.group(1).lower() or 'add' in m.group(1).lower():
            print(f"  data-{m.group(1)}: {m.group(2)[:80]}")
    # Look for nav links
    for m in re.finditer(r'href="(/[a-zA-Z][a-zA-Z0-9_-]+)"', d):
        if 'submit' in m.group(1).lower() or 'add' in m.group(1).lower() or 'new' in m.group(1).lower():
            print(f"  nav: {m.group(1)}")
