#!/usr/bin/env python3
"""Check Open-Aeon PR #2 and AgentPipe PR #1941 contents + look for ways to improve them + check x402.org."""
import json, urllib.request, urllib.error, re, subprocess, os, base64

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

# 1) Open-Aeon PR #2
print("=" * 60)
print("OPEN-AEON PR #2 (50 USDC)")
print("=" * 60)
pr = gh("repos/jessedaustin93/Open-Aeon/pulls/2")
if pr:
    print(f"  title: {pr.get('title')}")
    print(f"  state: {pr.get('state')}, draft: {pr.get('draft')}, mergeable: {pr.get('mergeable')}")
    print(f"  created: {pr.get('created_at')[:19]}")
    print(f"  additions: {pr.get('additions')}, deletions: {pr.get('deletions')}")
    print(f"  changed_files: {pr.get('changed_files')}")
    print(f"  head: {pr.get('head',{}).get('ref')}  base: {pr.get('base',{}).get('ref')}")
    print(f"  body: {pr.get('body','')[:500]}")

# 2) AgentPipe PR #1941
print()
print("=" * 60)
print("AGENTPIPE PR #1941 (23 USDC)")
print("=" * 60)
pr = gh("repos/dwebagents/AgentPipe/pulls/1941")
if pr:
    print(f"  title: {pr.get('title')}")
    print(f"  state: {pr.get('state')}, draft: {pr.get('draft')}, mergeable: {pr.get('mergeable')}")
    print(f"  created: {pr.get('created_at')[:19]}")
    print(f"  additions: {pr.get('additions')}, deletions: {pr.get('deletions')}")
    print(f"  changed_files: {pr.get('changed_files')}")
    print(f"  head: {pr.get('head',{}).get('ref')}  base: {pr.get('base',{}).get('ref')}")
    print(f"  body: {pr.get('body','')[:500]}")
    # Check if comments
    comments = gh("repos/dwebagents/AgentPipe/pulls/1941/comments")
    if isinstance(comments, list):
        for c in comments[:5]:
            print(f"  comment by {c.get('user',{}).get('login','?')}: {c.get('body','')[:200]}")

# 3) Look at x402.org main page for community/registry
print()
print("=" * 60)
print("x402.org main page")
print("=" * 60)
s, d = fetch("https://x402.org")
if isinstance(d, str):
    print(f"  size: {len(d)}")
    # Find links to community/registry
    for m in re.finditer(r'href="([^"]+)"', d):
        u = m.group(1)
        if any(kw in u.lower() for kw in ['discord','telegram','twitter','x.com','community','registry','services']):
            print(f"  {u[:100]}")
    # Find text mentioning registry/discovery
    for kw in ['registry','directory','discover','browse','list of']:
        idx = d.lower().find(kw)
        if idx > 0:
            ctx = d[max(0,idx-50):idx+200].replace("\n", " ")
            print(f"  '{kw}': ...{ctx[:250]}...")

# 4) Find x402.org/facilitator
print()
print("=" * 60)
print("x402.org/facilitator")
print("=" * 60)
s, d = fetch("https://x402.org/facilitator")
print(f"  status: {s}, size: {len(d) if isinstance(d, str) else 'n/a'}")
if isinstance(d, str):
    for kw in ['endpoints','/verify','/settle','resources']:
        idx = d.lower().find(kw)
        if idx > 0:
            ctx = d[max(0,idx-30):idx+200].replace("\n", " ")
            print(f"  '{kw}': ...{ctx[:200]}...")
