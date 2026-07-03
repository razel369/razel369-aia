#!/usr/bin/env python3
"""Deep dive on CrowdedSea (on-chain bounty pool) + look at Frantic runx skill bounties + AIA Worker tail."""
import json, urllib.request, urllib.error, re, subprocess, time

def fetch(url, headers=None, method="GET", data=None, timeout=20):
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
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e:
        return -1, str(e)

def gh(path):
    try:
        r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            try: return json.loads(r.stdout)
            except: return r.stdout
        return None
    except: return None

# 1) CrowdedSea deep dive
print("=" * 60)
print("CrowdedSea — on-chain bounty pool")
print("=" * 60)
repo = gh("repos/turfptax/CrowdedSea")
if isinstance(repo, dict):
    print(f"  full: {repo.get('full_name')}")
    print(f"  desc: {repo.get('description','')[:200]}")
    print(f"  stars: {repo.get('stargazers_count')}, forks: {repo.get('forks_count')}")
    print(f"  topics: {repo.get('topics',[])}")
    print(f"  default_branch: {repo.get('default_branch')}")
    print(f"  html: {repo.get('html_url')}")

# Issues with bounty tag
print()
print("Open issues:")
issues = gh("repos/turfptax/CrowdedSea/issues?state=open&per_page=20")
if isinstance(issues, list):
    for i in issues[:10]:
        labels = [l.get("name","") for l in i.get("labels",[])]
        print(f"  #{i.get('number')} {i.get('title','')[:80]}")
        print(f"    labels: {labels}")
        print(f"    body[:200]: {i.get('body','')[:200]}")

# README
print()
print("README:")
s, d = fetch("https://raw.githubusercontent.com/turfptax/CrowdedSea/main/README.md")
if isinstance(d, str):
    print(d[:3000])

# 2) Frantic skill bounties — what's expected
print()
print("=" * 60)
print("FRANTIC SKILL BOUNTIES (#69, #70, #68, #65)")
print("=" * 60)
# Look at one in detail
for bid in ["65", "68", "69", "70"]:
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":bid}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if b:
            cp = b.get("claimProgress",{})
            print(f"  #{bid} ${b.get('priceUsd')} avail={cp.get('available')}/{cp.get('capacity')} {b.get('title','')[:60]}")
            print(f"    preflight: {b.get('criteria',{}).get('preflight','-')[:200]}")

# 3) AIA Worker tail check
print()
print("=" * 60)
print("AIA WORKER TAIL (look for callers)")
print("=" * 60)
# Tail last 50 log lines from worker
r = subprocess.run(["npx","wrangler","tail","aia-x402","--format","json","--once"],
                   capture_output=True, text=True, timeout=30, cwd=r"C:\Users\rmalk\projects\razel369-aia\cloudflare-worker")
print(f"  stdout: {r.stdout[:2000]}")
print(f"  stderr: {r.stderr[:500]}")
