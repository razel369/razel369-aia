#!/usr/bin/env python3
"""Check if AIA is in Cinderwright /discover + look for registration endpoint + APB format."""
import json, urllib.request, urllib.error

def fetch(url, headers=None):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e: return -1, str(e)

# 1) Search for AIA
print("=" * 60)
print("CINDERWRIGHT: search for AIA")
print("=" * 60)
for q in ["aia", "razel369", "rmalka06", "autonomous insight", "signal stream"]:
    s, d = fetch(f"https://api.ideafactorylab.org/discover?q={q}")
    if isinstance(d, dict):
        results = d.get("results",[]) or d.get("services",[]) or []
        print(f"\n  q={q}: {d.get('total','?')} results")
        for sv in results[:5]:
            print(f"    {sv.get('name','')[:50]} | {sv.get('url','')[:60]}")
        if not results:
            print(f"  (no matches)")

# 2) Get the discover API surface
print()
print("=" * 60)
print("CINDERWRIGHT: full discover response (first 200 results)")
print("=" * 60)
s, d = fetch("https://api.ideafactorylab.org/discover?q=ai&limit=200")
if isinstance(d, dict):
    print(f"  total: {d.get('total')}")
    results = d.get("results",[]) or []
    print(f"  returned: {len(results)}")
    # Show first 5
    for sv in results[:5]:
        print(f"\n  {sv.get('name','')[:50]}")
        print(f"    url: {sv.get('url','')[:70]}")
        print(f"    provider: {sv.get('provider','')[:40]}")
        print(f"    description: {sv.get('description','')[:120]}")
        print(f"    endpoints: {sv.get('endpoints',[])}")

# 3) Try to find registration/submission endpoints
print()
print("=" * 60)
print("CINDERWRIGHT: find registration endpoints")
print("=" * 60)
for path in ["/submit", "/register", "/services", "/add", "/post", "/api/services",
             "/api/register", "/api/submit", "/api/v1/services",
             "/bounties.json", "/.well-known/services.json", "/.well-known/x402"]:
    s, d = fetch(f"https://api.ideafactorylab.org{path}")
    if s != 404:
        print(f"  {s} {path}")
        if isinstance(d, str) and len(d) < 500:
            print(f"    {d[:200]}")

# 4) Look at the discover response structure
print()
print("=" * 60)
print("CINDERWRIGHT: response structure")
print("=" * 60)
s, d = fetch("https://api.ideafactorylab.org/discover?q=aia")
if isinstance(d, dict):
    # Get a sample full object
    if d.get("results"):
        sample = d["results"][0]
        print(f"  Sample service keys: {list(sample.keys())}")
        print(f"  Sample: {json.dumps(sample, indent=2)[:1500]}")
