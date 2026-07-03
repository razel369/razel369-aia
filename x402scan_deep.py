#!/usr/bin/env python3
"""DEEP DIVE on x402scan.com — find registration + services API."""
import json, urllib.request, urllib.error, re, time, base64

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

# 1) Get the register page
print("=" * 60)
print("x402scan.com /resources/register")
print("=" * 60)
s, d = fetch("https://x402scan.com/resources/register")
if isinstance(d, str):
    print(f"  status: {s}, size: {len(d)}")
    # Find form fields
    for m in re.finditer(r'name="([a-zA-Z0-9_-]+)"', d):
        print(f"  field: {m.group(1)}")
    for m in re.finditer(r'placeholder="([^"]+)"', d):
        print(f"  placeholder: {m.group(1)[:80]}")
    for m in re.finditer(r'<button[^>]+>([^<]+)</button>', d):
        print(f"  button: {m.group(1)[:60]}")
    # Find text mentioning x402
    for kw in ["x402","USDC","base","register","api","submit"]:
        idx = d.lower().find(kw)
        if idx > 0:
            print(f"  '{kw}' ctx: ...{d[max(0,idx-50):idx+200].replace(chr(10),' ')[:200]}...")

# 2) Try /v1/ endpoints with the base URL
print()
print("=" * 60)
print("x402scan.com /v1/ endpoints")
print("=" * 60)
for path in ["/v1/services","/v1/resources","/v1/list","/v1/registry","/v1/discover",
             "/v1/exa/search","/v1/search","/v1/firecrawl/scrape","/v1/firecrawl/","/v1/models"]:
    for base in ["https://x402scan.com", "https://api.x402scan.com"]:
        s, d = fetch(f"{base}{path}", headers={"Accept":"application/json"}, timeout=10)
        if s == 200:
            if isinstance(d, dict):
                print(f"  {s} {base}{path}  keys: {list(d.keys())[:5]}")
            elif isinstance(d, list):
                print(f"  {s} {base}{path}  list: {len(d)}")
            else:
                print(f"  {s} {base}{path}  ({len(d)}b)")
        elif s != 404 and s != 405:
            print(f"  {s} {base}{path}")

# 3) Get services list via /api/public/services
print()
print("=" * 60)
print("x402scan.com /api/public/services")
print("=" * 60)
for path in ["/api/public/services","/api/public/services?limit=20",
             "/api/public/services?offset=0&limit=20",
             "/api/public/resources",
             "/api/public/resources?limit=20"]:
    s, d = fetch(f"https://x402scan.com{path}", headers={"Accept":"application/json"}, timeout=15)
    if s == 200:
        if isinstance(d, dict):
            print(f"  {s} {path}  keys: {list(d.keys())[:5]}")
            for k, v in d.items():
                if isinstance(v, list):
                    print(f"    {k}: {len(v)} items")
                    for item in v[:2]:
                        print(f"      {json.dumps(item)[:200]}")
        elif isinstance(d, list):
            print(f"  {s} {path}  list: {len(d)}")
            for item in d[:2]:
                print(f"    {json.dumps(item)[:200]}")
    else:
        print(f"  {s} {path}")

# 4) Get one service detail to see schema
print()
print("=" * 60)
print("x402scan.com single service detail")
print("=" * 60)
s, d = fetch("https://x402scan.com/api/public/services/svc_d7ckgxr67fhf94sq8", timeout=10)
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])
