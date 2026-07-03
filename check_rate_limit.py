#!/usr/bin/env python3
"""Get Frantic retry header + update AIA dashboard + check status of bounties."""
import json, urllib.request, urllib.error, time, subprocess, os

def fetch(url, headers=None, method="GET", data=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
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
                return r.status, json.loads(text), dict(r.headers)
            except:
                return r.status, text, dict(r.headers)
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text), dict(e.headers) if hasattr(e,"headers") else {}
        except:
            return e.code, text, {}
    except Exception as e:
        return -1, str(e), {}

# 1) Get Frantic rate limit info
print("=" * 60)
print("Frantic rate limit details")
print("=" * 60)
s, d, h = fetch("https://gofrantic.com/v1/deliveries/preflight", method="POST", data={
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print(f"status: {s}")
print(f"headers:")
for k, v in h.items():
    if "rate" in k.lower() or "retry" in k.lower() or "x-" in k.lower():
        print(f"  {k}: {v}")
if isinstance(d, dict):
    print(f"error: {d.get('error')}")
    print(f"retry_after: {d.get('retry_after_seconds')}")
    print(f"data: {json.dumps(d, indent=2)[:1000]}")
