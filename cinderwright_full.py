#!/usr/bin/env python3
"""Find Cinderwright main website + try to register AIA + look for APB endpoints."""
import json, urllib.request, urllib.error, re, subprocess

def fetch(url, headers=None):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
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

# 1) Get Cinderwright main website
print("=" * 60)
print("CINDERWRIGHT: main website")
print("=" * 60)
for url in ["https://cinderwright.com", "https://cinderwright.xyz", "https://cinderwright.io", "https://cinderwright.ai", "https://www.cinderwright.com"]:
    s, d = fetch(url)
    if s == 200:
        print(f"  {s} {url}  ({len(d)}b)")
        if isinstance(d, str):
            # Find links
            for m in re.finditer(r'href="([^"]+)"', d):
                link = m.group(1)
                if "api" in link.lower() or "ideafactory" in link.lower() or "x402" in link.lower() or "discover" in link.lower() or "bount" in link.lower():
                    print(f"    link: {link[:100]}")
    else:
        print(f"  {s} {url}")

# 2) Search GitHub for Cinderwright
print()
print("=" * 60)
print("GITHUB: Cinderwright / ideafactorylab")
print("=" * 60)
r = subprocess.run(["gh","search","repos","ideafactorylab","--limit","5","--json","fullName,description,stargazersCount"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: 
        for repo in json.loads(r.stdout):
            print(f"  {repo.get('fullName')}: {repo.get('description','')[:80]} stars={repo.get('stargazersCount')}")
    except: pass
r = subprocess.run(["gh","search","repos","cinderwright","--limit","5","--json","fullName,description,stargazersCount"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try:
        for repo in json.loads(r.stdout):
            print(f"  {repo.get('fullName')}: {repo.get('description','')[:80]} stars={repo.get('stargazersCount')}")
    except: pass

# 3) Try various endpoints to submit AIA
print()
print("=" * 60)
print("CINDERWRIGHT: try to submit AIA")
print("=" * 60)
aia_service = {
    "name": "AIA Real-Time Signal Stream",
    "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
    "description": "Filtered curated AI/agent/crypto/finance signals from HN, GitHub, V2EX, dev.to, Lobsters. 40+ signals per run, scored and deduplicated.",
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
# Try POST endpoints
for path in ["/submit", "/register", "/add", "/service", "/services", "/services/submit",
             "/api/submit", "/api/register", "/api/services", "/api/service",
             "/api/v1/services", "/api/v1/submit", "/api/v1/register",
             "/discover/submit", "/add-service", "/publish"]:
    for method in ["POST", "PUT"]:
        s, d = fetch(f"https://api.ideafactorylab.org{path}", method=method, data=aia_service)
        if s not in [404, 405, 415]:
            print(f"  {method} {s} {path}")
            if isinstance(d, dict):
                print(f"    {json.dumps(d)[:300]}")
            elif isinstance(d, str) and len(d) < 300:
                print(f"    {d}")
        else:
            pass  # ignore 404/405/415
