#!/usr/bin/env python3
"""Verify URL + try different evidence structures."""
import json, urllib.request, urllib.error, subprocess, time

# 1) Fetch current evidence
url = "https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json"
print(f"Fetching: {url}")
req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    body = r.read().decode("utf-8")
    print(f"status: {r.status}, length: {len(body)}")
    data = json.loads(body)
    print(f"top-level keys: {list(data.keys())}")
    print(f"observations type: {type(data.get('observations')).__name__}, count: {len(data.get('observations',[]))}")
    print(f"first obs: {data.get('observations',[{}])[0] if data.get('observations') else 'NONE'}")

# 2) Try different structures
print()
print("=" * 60)
print("Test different evidence structures")
print("=" * 60)

# Hypothesis: the schema expects `observations` at top level of an outer wrapper
# OR expects specific observation shape
# Let me try preflight endpoint to test
preflight_url = "https://gofrantic.com/v1/deliveries/preflight"
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

# Try preflight
test_url = "https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json"
s, d = fetch("POST", preflight_url, {
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json={test_url}",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print(f"preflight: {s}")
print(json.dumps(d, indent=2)[:2000] if isinstance(d, dict) else d[:2000])
