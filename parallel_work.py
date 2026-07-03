#!/usr/bin/env python3
"""Parallel work: check Open-Aeon, AIA bazaar, agentic.market, bounties expansion."""
import json, urllib.request, urllib.error, base64, re, time

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

# 1) Open-Aeon PR #2 status
print("=" * 60)
print("Open-Aeon PR #2 status")
print("=" * 60)
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/pulls/2")
if s == 200:
    print(f"state: {d.get('state')}, merged: {d.get('merged')}, mergeable: {d.get('mergeable')}")
    print(f"title: {d.get('title')}")
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/issues/2/comments?per_page=10")
if s == 200:
    print(f"comments: {len(d)}")
    for c in d:
        print(f"  by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("  ---")

# 2) AIA Cloudflare Worker bazaar extension - read current source
print()
print("=" * 60)
print("AIA Worker source check")
print("=" * 60)
with open(r"C:\Users\rmalk\projects\razel369-aia\cloudflare-worker\src\index.js") as f:
    src = f.read()
print(f"size: {len(src)}")
# Check for bazaar extension
has_bazaar = "bazaar" in src.lower()
has_output_schema = "outputSchema" in src
print(f"has bazaar: {has_bazaar}")
print(f"has outputSchema: {has_output_schema}")

# 3) agentic.market direct submission attempt
print()
print("=" * 60)
print("agentic.market submission endpoints")
print("=" * 60)
endpoints = [
    "https://api.agentic.market/v1/services",
    "https://api.agentic.market/v1/services/register",
    "https://api.agentic.market/v1/submit",
    "https://agentic.market/api/services",
    "https://api.agentic.market/v1/bazaar",
    "https://api.agentic.market/v1/agents/register",
]
for url in endpoints:
    for method in ["GET","POST"]:
        try:
            req = urllib.request.Request(url, method=method,
                data=b"{}" if method == "POST" else None,
                headers={"Content-Type":"application/json","User-Agent":"razel369-aia/1.0","Accept":"application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                print(f"  {method} {url} → {r.status} (len {len(r.read().decode('utf-8','replace'))})")
        except urllib.error.HTTPError as e:
            print(f"  {method} {url} → {e.code}")
        except Exception as e:
            print(f"  {method} {url} → err: {e}")

# 4) Check if agentic.market has a sitemap or list with submission form
print()
print("=" * 60)
print("agentic.market /submit or add-service form")
print("=" * 60)
s, body, _ = fetch("https://agentic.market") if False else (None, "", {})
import urllib.request
req = urllib.request.Request("https://agentic.market", headers={"User-Agent":"razel369-aia/1.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    body = r.read().decode("utf-8", errors="replace")
    # Find submit / add your service
    for kw in ["submit","add your","add a service","list your service","/submit","/new","/add"]:
        for m in re.finditer(kw, body, re.IGNORECASE):
            ctx = body[max(0,m.start()-100):min(len(body),m.end()+200)].replace("\n"," ")
            print(f"  '{kw}': ...{ctx[:300]}...")
            break
    # Find form actions
    for m in re.finditer(r'action="([^"]+)"', body):
        print(f"  form action: {m.group(1)}")

# 5) Search docs.cdp.coinbase.com for submission process
print()
print("=" * 60)
print("CDP x402 docs - submission process")
print("=" * 60)
for url in ["https://docs.cdp.coinbase.com/x402/bazaar", "https://docs.cdp.coinbase.com/x402/discovery", "https://docs.cdp.coinbase.com/x402/welcome", "https://docs.cdp.coinbase.com/x402/quickstart"]:
    s, body, _ = fetch(url)
    print(f"  {s} {len(body)}b  {url}")
    if s == 200:
        text = re.sub(r"<[^>]+>"," ", body)
        text = re.sub(r"\s+"," ", text)
        for kw in ["submit", "add your", "list", "bazaar", "register"]:
            m = re.search(kw, text, re.IGNORECASE)
            if m:
                ctx = text[max(0,m.start()-100):min(len(text),m.end()+200)]
                print(f"    '{kw}': ...{ctx[:300]}...")
                break

# 6) Find more open bounties via new GitHub search
print()
print("=" * 60)
print("More bounties (GrantFox, Opire, Tari, etc.)")
print("=" * 60)
import urllib.parse
queries = [
    "label:bounty is:issue is:open USDC",
    "label:bounty is:issue is:open USD",
    "label:Opire is:issue is:open",
    "[bounty] is:issue is:open",
    "Fixes #1887",
    "is:issue is:open 0x833ca7d"
]
for q in queries[:3]:
    s, d = gh("GET", f"/search/issues?q={urllib.parse.quote(q)}&per_page=10")
    if s == 200:
        items = d.get("items", [])
        print(f"  q='{q[:40]}': {len(items)} issues")
        for it in items[:5]:
            print(f"    #{it.get('number')} {it.get('repository_url').split('/')[-1]} [{','.join(l.get('name') for l in it.get('labels',[]))}] {it.get('title')[:60]}")
