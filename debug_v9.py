#!/usr/bin/env python3
"""Debug v9 (real one) more."""
import json, urllib.request, urllib.error

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

# Preflight my real v9
s, d = fetch("POST", "https://gofrantic.com/v1/deliveries/preflight", {
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print("=" * 60)
print("Full preflight response")
print("=" * 60)
print(json.dumps(d, indent=2)[:3000] if isinstance(d, dict) else d[:2000])

# Now compare with v9b (which passed)
print()
print("=" * 60)
print("v9b (which passed)")
print("=" * 60)
s2, d2 = fetch("POST", "https://gofrantic.com/v1/deliveries/preflight", {
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/test_v9b_short.json",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print(json.dumps(d2, indent=2)[:3000] if isinstance(d2, dict) else d2[:2000])
