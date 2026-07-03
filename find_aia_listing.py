#!/usr/bin/env python3
"""Check if AIA is on x402scan + look for x402 community channels + try one more way to list."""
import json, urllib.request, urllib.error, re, base64

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

# 1) Search x402scan for AIA
print("=" * 60)
print("x402scan search for AIA")
print("=" * 60)
for q in ["aia","razel369","rmalka06","signal stream","agent feed","autonomous insight"]:
    s, d = fetch(f"https://www.x402scan.com/resources?q={q}")
    if isinstance(d, str):
        # Look for service entries
        count = len(re.findall(r'svc_[a-z0-9]+', d))
        has_aia = "aia-x402" in d.lower() or "razel369" in d.lower() or "rmalka06" in d.lower()
        print(f"  q={q}: status={s} size={len(d)} svc_ids={count} has_aia={has_aia}")

# 2) Look at x402 ecosystem on GitHub
print()
print("=" * 60)
print("x402 ECOSYSTEM REPOS")
print("=" * 60)
for path in [
    "https://api.github.com/repos/coinbase/x402",
    "https://api.github.com/repos/coinbase/x402/contents",
]:
    s, d = fetch(path, headers={"Accept":"application/vnd.github+json"})
    if isinstance(d, dict):
        if "name" in d:
            print(f"  {d.get('full_name')} - {d.get('description','')[:100]}")
            print(f"    stars: {d.get('stargazers_count')}, topics: {d.get('topics')}")
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, dict):
                    print(f"    {item.get('name','')[:50]} ({item.get('type','')})")

# 3) Look at x402 Discord/Telegram
print()
print("=" * 60)
print("x402 COMMUNITY CHANNELS")
print("=" * 60)
for url in [
    "https://discord.gg/x402",
    "https://discord.gg/cdpx402",
    "https://t.me/x402",
    "https://t.me/coinbasex402",
    "https://x.com/x402",
    "https://x.com/coinbasex402",
]:
    s, d = fetch(url, timeout=8)
    if s in [200,301,302]:
        print(f"  {s} {url}")

# 4) Look at AIA Worker on agentic.market with a different query
print()
print("=" * 60)
print("agentic.market: search for AI signal services")
print("=" * 60)
for q in ["ai signal","signal feed","hn feed","trending","agent feed","research signal"]:
    s, d = fetch(f"https://api.agentic.market/v1/services?search={q.replace(' ','+')}&limit=10",
                 headers={"Accept":"application/json"})
    if isinstance(d, dict):
        services = d.get("services",[])
        # Look for similar services
        for s2 in services[:10]:
            n = s2.get("name","")
            u = s2.get("url","")
            p = s2.get("price")
            if any(kw in (n+u).lower() for kw in ["signal","feed","hn","trending","research","news"]):
                print(f"  [MATCH] {n} ${p} {u[:60]}")
        if not any(any(kw in (s2.get('name','')+s2.get('url','')).lower() for kw in ["signal","feed","hn","trending"]) for s2 in services[:10]):
            print(f"  q={q}: {len(services)} services (none matching signal/feed/hn)")
    else:
        print(f"  q={q}: status={s}")
