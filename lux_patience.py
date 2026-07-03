#!/usr/bin/env python3
"""Look at lux #67 + #62 with patience."""
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
                time.sleep(15 * (2**i))
                continue
            return e.code, e.read().decode("utf-8", errors="replace")[:300]
        except Exception as e:
            return -1, str(e)
    return -1, "retries exceeded"

# Wait a bit for rate limit
print("Waiting 30s for GitHub rate limit reset...")
time.sleep(30)
print("Done waiting.")

# Get lux #67 (Telegram Analytics $1,200) + a few others
for n in [67, 62, 65, 95, 97, 56, 100]:
    s, d = gh(f"/repos/Spectral-Finance/lux/issues/{n}")
    if s == 200:
        print(f"\n=== #{n} {d.get('title')} ===")
        print(f"state: {d.get('state')}, comments: {d.get('comments')}")
        print(f"labels: {[l.get('name') for l in d.get('labels',[])]}")
        body = d.get("body","") or ""
        print(f"body: {body[:1500]}")
        # Get comments
        s2, d2 = gh(f"/repos/Spectral-Finance/lux/issues/{n}/comments?per_page=10")
        if s2 == 200:
            for c in d2:
                cb = c.get("body","") or ""
                if "USDC" in cb or "0x" in cb or "payout" in cb.lower() or "wallet" in cb.lower() or "address" in cb.lower() or "Algora" in cb:
                    print(f"  cmt by {c.get('user',{}).get('login')}: {cb[:500]}")
                    print("  ---")
    else:
        print(f"\n=== #{n} {s} ===")
    time.sleep(2)
