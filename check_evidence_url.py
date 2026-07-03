#!/usr/bin/env python3
"""Verify URL content + preflight again."""
import json, urllib.request, urllib.error

url = "https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json"
print(f"Fetching: {url}")
req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    body = r.read().decode("utf-8")
    print(f"status: {r.status}, length: {len(body)}")
    data = json.loads(body)
    print(f"keys: {list(data.keys())}")
    print(f"observations: type={type(data.get('observations')).__name__}, count={len(data.get('observations',[]))}")
    print(f"summary length: {len(data.get('summary',''))}")
    if data.get('observations'):
        print(f"first obs: {data['observations'][0]}")
        print(f"first obs keys: {list(data['observations'][0].keys())}")

# Now preflight this exact URL
print()
print("=" * 60)
print("Preflight on runx_love_evidence.json")
print("=" * 60)

def fetch(method, url, data=None, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
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

s, d = fetch("POST", "https://gofrantic.com/v1/deliveries/preflight", {
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json={url}",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print(f"preflight: {s}")
if isinstance(d, dict):
    pre = d.get("preflight", d)
    print(f"ok: {pre.get('ok')}")
    for e in pre.get("errors", []):
        print(f"  err: {e.get('code','?')}: {e.get('message','')[:200]}")
