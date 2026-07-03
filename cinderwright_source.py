#!/usr/bin/env python3
"""Look at cinderwright-ai/cinderwright-api source to find registration endpoint + APB format."""
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

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

# 1) Get the repo info
print("=" * 60)
print("cinderwright-ai/cinderwright-api")
print("=" * 60)
repo = gh("repos/cinderwright-ai/cinderwright-api")
if isinstance(repo, dict):
    print(f"  desc: {repo.get('description','')}")
    print(f"  stars: {repo.get('stargazers_count')}, html: {repo.get('html_url')}")
    print(f"  homepage: {repo.get('homepage')}")
    print(f"  topics: {repo.get('topics',[])}")
    print(f"  pushed: {repo.get('pushed_at')}")

# 2) Look at README
print()
print("=" * 60)
print("README")
print("=" * 60)
r = subprocess.run(["gh","api","repos/cinderwright-ai/cinderwright-api/contents/README.md"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try:
        j = json.loads(r.stdout)
        content = base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
        print(content[:5000])
    except: pass

# 3) List all files
print()
print("=" * 60)
print("REPO FILES")
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

# 4) Look at server.js or main entry
print()
print("=" * 60)
print("MAIN ENTRY (likely server.js or similar)")
print("=" * 60)
for fname in ["server.js", "index.js", "app.js", "src/server.js", "src/index.js", "src/app.js", "cinderwright-api/server.js"]:
    r = subprocess.run(["gh","api",f"repos/cinderwright-ai/cinderwright-api/contents/{fname}"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try:
            j = json.loads(r.stdout)
            content = base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
            print(f"\n  --- {fname} ---")
            print(content[:5000])
        except: pass

# 5) Try POST to various submit endpoints
print()
print("=" * 60)
print("TRY SUBMIT ENDPOINTS")
print("=" * 60)
aia_service = {
    "name": "AIA Real-Time Signal Stream",
    "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
    "description": "Filtered curated AI/agent/crypto signals from HN, GitHub, V2EX, dev.to, Lobsters.",
    "provider": "razel369-aia",
    "endpoints": [
        {"path":"/v1/signals","method":"GET","price":"$0.01","network":"eip155:8453","category":"ai"},
        {"path":"/v1/digest","method":"GET","price":"$0.003","network":"eip155:8453","category":"ai"},
        {"path":"/v1/alerts","method":"GET","price":"$0.005","network":"eip155:8453","category":"ai"}
    ],
    "payment": {
        "protocol":"x402",
        "network":"eip155:8453",
        "payTo":"0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
    }
}
for path in ["/api/services", "/api/submit", "/services", "/api/v1/services", "/api/v1/submit",
             "/submit", "/add", "/api/discover", "/api/v1/discover", "/register",
             "/api/agents", "/api/agent", "/api/manifest", "/.well-known/services.json",
             "/api/services/submit", "/api/service", "/api/v1/service"]:
    for method in ["POST", "PUT"]:
        s, d = fetch(f"https://api.ideafactorylab.org{path}", method=method, data=aia_service)
        if s not in [404, 405, 415, 400]:
            print(f"  {method} {s} {path}")
            if isinstance(d, dict):
                print(f"    {json.dumps(d)[:300]}")
            elif isinstance(d, str) and len(d) < 500:
                print(f"    {d[:300]}")
