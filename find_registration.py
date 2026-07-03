#!/usr/bin/env python3
"""Find x402scan.com registration mechanism + look at x402list.com + AIA 402 check."""
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

# 1) Download x402scan register page and look at all API calls
print("=" * 60)
print("x402scan.com /resources/register — find action")
print("=" * 60)
s, d = fetch("https://x402scan.com/resources/register",
             headers={"Accept":"text/html","User-Agent":"Mozilla/5.0"})
if isinstance(d, str):
    # Find next.js data with form action / handler
    for m in re.finditer(r'\\"href\\":\\"(/[a-zA-Z0-9_/-]+)\\"', d):
        if 'api' in m.group(1) or 'submit' in m.group(1) or 'service' in m.group(1) or 'register' in m.group(1):
            print(f"  href: {m.group(1)}")
    # Look for the form action / input
    for m in re.finditer(r'\\"action\\":\\"([^"]+)\\"', d):
        print(f"  action: {m.group(1)}")
    for m in re.finditer(r'action="([^"]+)"', d):
        print(f"  form action: {m.group(1)}")
    # Find any "input" pattern (client-side)
    for m in re.finditer(r'<input[^>]+>', d):
        s2 = m.group(0)
        if 'hidden' in s2 or 'name=' in s2:
            print(f"  input: {s2[:200]}")

# 2) Look at x402list.com
print()
print("=" * 60)
print("x402list.com")
print("=" * 60)
s, d = fetch("https://x402list.com", headers={"Accept":"text/html"})
if isinstance(d, str):
    print(f"  size: {len(d)}")
    for m in re.finditer(r'href="([^"]+)"', d):
        u = m.group(1)
        if 'add' in u.lower() or 'submit' in u.lower() or 'service' in u.lower() or 'register' in u.lower():
            print(f"  link: {u[:80]}")
    for m in re.finditer(r'src="(/_next/[^"]+\.js[^"]*)"', d):
        print(f"  js: {m.group(1)[:100]}")

# 3) Look at x402discovery.com
print()
print("=" * 60)
print("x402discovery.com")
print("=" * 60)
s, d = fetch("https://x402discovery.com", headers={"Accept":"text/html"})
if isinstance(d, str):
    print(f"  size: {len(d)}")
    for m in re.finditer(r'href="([^"]+)"', d):
        u = m.group(1)
        if any(kw in u.lower() for kw in ['add','submit','service','register','api']):
            print(f"  link: {u[:80]}")
    # Check for API endpoints
    for m in re.finditer(r'(/api/[a-zA-Z0-9_/-]+)', d):
        print(f"  api: {m.group(1)}")

# 4) Get AIA 402 with proper Accept header
print()
print("=" * 60)
print("AIA 402 with proper headers")
print("=" * 60)
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/signals",
             headers={"Accept":"text/html,application/json,*/*",
                      "User-Agent":"Mozilla/5.0 (X11; Linux x86_64)"})
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])
elif isinstance(d, str):
    print(f"  raw: {d[:500]}")
