#!/usr/bin/env python3
"""Multi-pronged attack: HN submit, look for new Frantic bounties, look for x402 services."""
import json, urllib.request, urllib.error, re, urllib.parse, time

def fetch(url, headers=None, method="GET", data=None, timeout=30):
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

# 1) HN submit attempt
print("=" * 60)
print("HN submit attempt")
print("=" * 60)
hn_url = "https://news.ycombinator.com/submit"
hn_post_url = "https://github.com/razel369/razel369-aia"
hn_title = "Show HN: AIA \u2013 an AI agent that pays its own bills (x402 paid API, $0 budget)"

# First, GET the form to get any session cookies + see fields
import http.cookiejar
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
try:
    r = opener.open(hn_url, timeout=10)
    body = r.read().decode("utf-8")
    print(f"  GET submit: {r.status}, {len(body)} bytes")
    # Find hmac or token
    hmac_m = re.search(r'<input[^>]+name="hmac"[^>]+value="([^"]+)"', body)
    print(f"  hmac: {hmac_m.group(1)[:30] if hmac_m else 'NONE'}")
    # Check for captcha
    if "captcha" in body.lower() or "recaptcha" in body.lower():
        print("  CAPTCHA detected - can't auto-submit")
except Exception as e:
    print(f"  err: {e}")

# 2) Find similar Show HN posts to learn the format
print()
print("=" * 60)
print("Recent Show HN posts about x402")
print("=" * 60)
s, d = fetch("https://hn.algolia.com/api/v1/search?query=x402+OR+%22AI+agent%22&tags=story&hitsPerPage=20")
if s == 200:
    hits = d.get("hits", [])
    print(f"  {len(hits)} hits")
    for h in hits[:10]:
        title = h.get("title","")
        ts = h.get("created_at","")
        if "x402" in title.lower() or "agent" in title.lower() or "bount" in title.lower():
            print(f"  {ts[:10]}  {title[:80]}")
            print(f"    {h.get('url','')}")

# 3) Find more Frantic-style platforms
print()
print("=" * 60)
print("Find more agentic bounty platforms")
print("=" * 60)
# GitHub search for x402 + bounty
s, d = fetch("https://api.github.com/search/repositories?q=x402+bounty&per_page=10")
if s == 200:
    for it in d.get("items",[])[:10]:
        print(f"  ★{it.get('stargazers_count',0):>4}  {it.get('full_name')}: {it.get('description','')[:80]}")

# 4) Look at BoltzPay (mentioned in HN) - similar to AIA
print()
print("=" * 60)
print("BoltzPay (x402 pay library)")
print("=" * 60)
s, d = fetch("https://api.github.com/repos/leventilo/boltzpay")
if s == 200:
    print(f"  desc: {d.get('description','')[:200]}")
    print(f"  ★ {d.get('stargazers_count')}")
s, d = fetch("https://api.github.com/repos/leventilo/boltzpay/readme")
if s == 200:
    import base64
    rd = base64.b64decode(d.get("content","")).decode("utf-8")
    print(rd[:2000])

# 5) X402-Mesh
print()
print("=" * 60)
print("X402-Mesh")
print("=" * 60)
s, d = fetch("https://api.github.com/repos/StartupHub-AI/x402-mesh")
if s == 200:
    print(f"  desc: {d.get('description','')[:200]}")
    print(f"  ★ {d.get('stargazers_count')}")
s, d = fetch("https://api.github.com/repos/StartupHub-AI/x402-mesh/readme")
if s == 200:
    import base64
    rd = base64.b64decode(d.get("content","")).decode("utf-8")
    print(rd[:2000])
