#!/usr/bin/env python3
"""Quick check lux #67 + a few others."""
import json, urllib.request, urllib.error, time

def gh(path):
    try:
        req = urllib.request.Request("https://api.github.com" + path,
            headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:200]
    except Exception as e:
        return -1, str(e)

# Just check #67 first
s, d = gh("/repos/Spectral-Finance/lux/issues/67")
print(f"status: {s}")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}, comments: {d.get('comments')}")
    print(f"body:\n{d.get('body','')}")

# Check a few specific ones in parallel via batch
print()
print("=" * 60)
print("Batch fetch multiple issues")
print("=" * 60)
import concurrent.futures
issues_to_check = [54, 55, 56, 62, 65, 66, 67, 85, 95, 97, 100, 1428]
def fetch_one(n):
    s, d = gh(f"/repos/Spectral-Finance/lux/issues/{n}")
    if s == 200:
        return n, d.get("title",""), (d.get("body","") or "")[:300]
    return n, None, None
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    futures = [ex.submit(fetch_one, n) for n in issues_to_check]
    for f in concurrent.futures.as_completed(futures):
        n, title, body = f.result()
        print(f"\n#{n} {title}")
        if body:
            print(body)
