#!/usr/bin/env python3
"""Get lux #67 with retry."""
import json, urllib.request, urllib.error, time

def gh(path, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request("https://api.github.com" + path,
                headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                wait = 5 * (2**i)
                print(f"  rate-limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            return e.code, e.read().decode("utf-8", errors="replace")[:300]
        except Exception as e:
            return -1, str(e)
    return -1, "retries exceeded"

# Get all relevant lux issues
for n in [54, 55, 56, 62, 63, 64, 65, 66, 67, 85, 86, 87, 94, 95, 96, 97, 100, 1428, 14089]:
    s, d = gh(f"/repos/Spectral-Finance/lux/issues/{n}")
    if s == 200:
        title = d.get("title","")
        body = d.get("body","") or ""
        print(f"\n=== #{n} {title} ===")
        print(body[:800])
        s2, d2 = gh(f"/repos/Spectral-Finance/lux/issues/{n}/comments?per_page=5")
        if s2 == 200:
            for c in d2:
                cb = c.get("body","") or ""
                if "USDC" in cb or "0x" in cb or "payout" in cb.lower() or "wallet" in cb.lower() or "address" in cb.lower():
                    print(f"  cmt by {c.get('user',{}).get('login')}: {cb[:400]}")
        time.sleep(0.5)
    else:
        print(f"\n=== #{n} {s} ===")
