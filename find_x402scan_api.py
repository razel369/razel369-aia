#!/usr/bin/env python3
"""Find x402scan form submit URL from the bundled JS."""
import json, urllib.request, urllib.error, re, base64

def fetch(url, headers=None, timeout=20):
    h = {"User-Agent":"Mozilla/5.0"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return -1, str(e)

# 1) Get the main page
s, d = fetch("https://www.x402scan.com/resources/register")
print(f"Main page: {s}, size: {len(d)}")

# 2) Find ALL JS chunks referenced
print()
print("JS chunks referenced:")
js_chunks = set()
for m in re.finditer(r'(/_next/static/chunks/[a-zA-Z0-9_-]+\.js(?:\?[^"]*)?)', d):
    js_chunks.add(m.group(1))
for m in re.finditer(r'"(/_next/static/chunks/[^"]+\.js[^"]*)"', d):
    js_chunks.add(m.group(1))

# 3) Download each and search for /api/ or /register or fetch calls
print(f"  found {len(js_chunks)} chunks")
all_calls = set()
for chunk in list(js_chunks)[:30]:
    s2, c = fetch(f"https://www.x402scan.com{chunk}")
    if s2 == 200:
        # Look for API calls
        for m in re.finditer(r'(?:fetch|axios)[^,]*["\']([^"\']+)["\']', c):
            u = m.group(1)
            if u.startswith("/") and "api" in u.lower():
                all_calls.add(u)
        # Look for form submission
        for m in re.finditer(r'action:\s*["\']([^"\']+)["\']', c):
            all_calls.add(m.group(1))
        for m in re.finditer(r'url:\s*["\']([^"\']+)["\']', c):
            u = m.group(1)
            if u.startswith("/"):
                all_calls.add(u)

print()
print(f"  All API calls found: {len(all_calls)}")
for u in sorted(all_calls):
    print(f"    {u[:120]}")
