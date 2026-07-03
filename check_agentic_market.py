#!/usr/bin/env python3
"""Check + submit AIA to agentic.market + verify bazaar extension."""
import json, sys, urllib.request, urllib.error, base64

# 1) Check if AIA is already in agentic.market
print("=" * 60)
print("1. Check if AIA is listed on agentic.market")
print("=" * 60)
for q in ["AIA", "razel369", "Autonomous Insight", "insight", "agent", "signal"]:
    try:
        url = f"https://api.agentic.market/v1/services/search?q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={"Accept":"application/json","User-Agent":"razel369-aia/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
            services = d.get("services", d if isinstance(d, list) else [])
            print(f"  q={q!r:<25}  matches={len(services)}")
            for s in services[:3]:
                if any(k in (s.get("name","")+s.get("description","")).lower() for k in ["aia","razel","insight","autonomous"]):
                    print(f"    *** MATCH: {s.get('name','')}  {s.get('description','')[:80]}")
    except urllib.error.HTTPError as e:
        print(f"  q={q!r:<25}  HTTP {e.code}")
    except Exception as e:
        print(f"  q={q!r:<25}  err: {e}")

# 2) Check the bazaar extension on my own worker
print()
print("=" * 60)
print("2. Verify my Worker's bazaar extension")
print("=" * 60)
try:
    req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/v1/signals",
                                 headers={"Accept":"application/json","User-Agent":"razel369-aia/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"  status: {r.status}  (expected 402)")
    except urllib.error.HTTPError as e:
        if e.code == 402:
            phdr = e.headers.get("PAYMENT-REQUIRED","")
            if phdr:
                decoded = json.loads(base64.b64decode(phdr).decode("utf-8"))
                print(f"  402 PAYMENT-REQUIRED decoded:")
                print(json.dumps(decoded, indent=2)[:2000])
                # Check for extensions.bazaar
                ext = decoded.get("accepts",[{}])[0].get("extra",{}).get("bazaar",{})
                if not ext:
                    # Try other locations
                    ext = decoded.get("accepts",[{}])[0].get("extensions",{}).get("bazaar",{})
                if ext:
                    print(f"\n  BAZAAR EXTENSION FOUND:")
                    print(json.dumps(ext, indent=2)[:1500])
                else:
                    print(f"\n  No bazaar extension found in PAYMENT-REQUIRED")
        else:
            print(f"  unexpected status: {e.code}")
except Exception as e:
    print(f"  err: {e}")

# 3) Check the .well-known/x402 manifest
print()
print("=" * 60)
print("3. Check .well-known/x402 manifest")
print("=" * 60)
try:
    req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/.well-known/x402",
                                 headers={"Accept":"application/json","User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode("utf-8")
        print(f"  status: {r.status}")
        try:
            d = json.loads(body)
            print(json.dumps(d, indent=2)[:3000])
        except:
            print(body[:1500])
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}")
except Exception as e:
    print(f"  err: {e}")
