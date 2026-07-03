#!/usr/bin/env python3
"""SUBMIT AIA to Cinderwright + set up proxy account + look for bounty endpoints."""
import json, urllib.request, urllib.error, subprocess, base64

def fetch(url, method="GET", data=None, headers=None):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
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

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

# 1) SUBMIT AIA via /submit (per README)
print("=" * 60)
print("CINDERWRIGHT: SUBMIT AIA")
print("=" * 60)
submit_payload = {
    "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
    "name": "AIA Real-Time Signal Stream",
    "description": "Filtered curated AI/agent/crypto/finance signals from HN, GitHub trending, V2EX, dev.to, Lobsters. 40+ signals per run, scored and deduplicated. Affordable x402 micro-payments on Base ($0.01 signals, $0.003 digest, $0.005 alerts).",
    "provider": "razel369-aia",
    "operator": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
}
s, d = fetch("https://api.ideafactorylab.org/submit", method="POST", data=submit_payload)
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])
else:
    print(f"  raw: {d[:1000]}")

# 2) Setup proxy account
print()
print("=" * 60)
print("CINDERWRIGHT: SETUP PROXY")
print("=" * 60)
s, d = fetch("https://api.ideafactorylab.org/proxy/setup", method="POST", data={"wallet": WALLET})
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])
else:
    print(f"  raw: {d[:1000]}")

# 3) Check the test endpoint to see if AIA is now indexed
print()
print("=" * 60)
print("CINDERWRIGHT: search for AIA after submission")
print("=" * 60)
for q in ["aia", "razel369", "rmalka06", "signal stream", "autonomous insight"]:
    s, d = fetch(f"https://api.ideafactorylab.org/discover?q={q}")
    if isinstance(d, dict):
        results = d.get("results",[]) or []
        print(f"  q={q}: total={d.get('total')} matches={len(results)}")
        for sv in results[:3]:
            print(f"    {sv.get('name','')[:50]} | {sv.get('url','')[:60]}")

# 4) Check the /budget endpoint
print()
print("=" * 60)
print("CINDERWRIGHT: budget endpoint")
print("=" * 60)
s, d = fetch(f"https://api.ideafactorylab.org/budget?wallet={WALLET}")
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:1000])

# 5) Look at the cinderwright-api source for the actual submit handler
print()
print("=" * 60)
print("CINDERWRIGHT: source code (submit handler)")
print("=" * 60)
r = subprocess.run(["gh","api","repos/cinderwright-ai/cinderwright-api/git/trees/HEAD?recursive=1"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try:
        j = json.loads(r.stdout)
        files = j.get("tree",[])
        for f in files[:30]:
            print(f"  {f.get('type','?')} {f.get('path','?')}")
    except: pass
