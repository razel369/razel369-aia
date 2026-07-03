#!/usr/bin/env python3
"""Look at agent bounty arena + x402 task board + boost AIA visibility."""
import json, urllib.request, urllib.error, base64, time

def gh(path, retries=2):
    for i in range(retries):
        try:
            req = urllib.request.Request("https://api.github.com" + path,
                headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                time.sleep(5 * (2**i))
                continue
            return e.code, e.read().decode("utf-8", errors="replace")[:300]
        except Exception as e:
            return -1, str(e)
    return -1, "retries"

# 1) TheBarmaEffect arena
print("=" * 60)
print("TheBarmaEffect/origin-agent-bounty-hunter")
print("=" * 60)
s, d = gh("/repos/TheBarmaEffect/origin-agent-bounty-hunter")
if s == 200:
    print(f"  desc: {d.get('description','')[:300]}")
    print(f"  ★ {d.get('stargazers_count')}, fork: {d.get('forks_count')}")
    print(f"  language: {d.get('language')}")
    print(f"  created: {d.get('created_at')}")
s, d = gh("/repos/TheBarmaEffect/origin-agent-bounty-hunter/readme")
if s == 200:
    rd = base64.b64decode(d.get("content","")).decode("utf-8")
    print(f"  README:\n{rd[:3000]}")
s, d = gh("/repos/TheBarmaEffect/origin-agent-bounty-hunter/issues?state=open&per_page=20")
if s == 200:
    for it in d:
        if "pull_request" in it: continue
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        print(f"    body: {(it.get('body','') or '')[:300]}")

# 2) secret-mars x402 task board
print()
print("=" * 60)
print("secret-mars/x402-task-board")
print("=" * 60)
s, d = gh("/repos/secret-mars/x402-task-board")
if s == 200:
    print(f"  desc: {d.get('description','')[:300]}")
    print(f"  ★ {d.get('stargazers_count')}")
s, d = gh("/repos/secret-mars/x402-task-board/readme")
if s == 200:
    rd = base64.b64decode(d.get("content","")).decode("utf-8")
    print(f"  README:\n{rd[:3000]}")

# 3) RECTOR-LABS sap-x402-agent
print()
print("=" * 60)
print("RECTOR-LABS/sap-x402-agent")
print("=" * 60)
s, d = gh("/repos/RECTOR-LABS/sap-x402-agent")
if s == 200:
    print(f"  desc: {d.get('description','')[:300]}")
    print(f"  ★ {d.get('stargazers_count')}")
s, d = gh("/repos/RECTOR-LABS/sap-x402-agent/readme")
if s == 200:
    rd = base64.b64decode(d.get("content","")).decode("utf-8")
    print(f"  README:\n{rd[:3000]}")

# 4) Try to find an Algora-style API via the public console
print()
print("=" * 60)
print("Algora console API discovery")
print("=" * 60)
# The console.algora.io is an SPA. Let's see what JS bundles it loads
import urllib.request
import re
try:
    req = urllib.request.Request("https://console.algora.io/", headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read().decode("utf-8")
        # Find script srcs
        for m in re.finditer(r'src="([^"]+)"', body):
            src = m.group(1)
            if src.startswith("/"):
                src = "https://console.algora.io" + src
            print(f"  script: {src[:150]}")
except Exception as e:
    print(f"  err: {e}")
