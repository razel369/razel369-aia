#!/usr/bin/env python3
"""Verify current evidence.json content."""
import urllib.request, json

url = "https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json"
req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0","Cache-Control":"no-cache"})
with urllib.request.urlopen(req, timeout=15) as r:
    body = r.read().decode("utf-8")
print(f"size: {len(body)}")
print(f"starts with: {body[:200]}")
data = json.loads(body)
print(f"\ntop-level summary:")
print(f"  {data.get('summary','')[:300]}")
print(f"\nobservations count: {len(data.get('observations',[]))}")
if data.get('observations'):
    print(f"\nfirst obs:")
    print(json.dumps(data['observations'][0], indent=2)[:600])
