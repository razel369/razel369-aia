#!/usr/bin/env python3
"""Check PR #1941 actual diff + see what file is expected + look at issue #1580."""
import json, urllib.request, urllib.error, subprocess, re

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

# 1) Get PR #1941 files
print("=" * 60)
print("AGENTPIPE PR #1941 — files + diff")
print("=" * 60)
files = gh("repos/dwebagents/AgentPipe/pulls/1941/files")
if isinstance(files, list):
    for f in files:
        print(f"  {f.get('status')} {f.get('filename')}  +{f.get('additions')} -{f.get('deletions')}")
        patch = f.get('patch','')
        if patch:
            print(f"    patch: {patch[:500]}")
print()
print("  Diff (raw):")
diff = gh("repos/dwebagents/AgentPipe/pulls/1941.diff")
if isinstance(diff, str):
    print(diff[:2000])
elif isinstance(diff, dict):
    print(json.dumps(diff, indent=2)[:2000])

# 2) Look at issue #1580 to see what file is expected
print()
print("=" * 60)
print("ISSUE #1580 (the bounty)")
print("=" * 60)
issue = gh("repos/dwebagents/AgentPipe/issues/1580")
if issue:
    print(f"  title: {issue.get('title')}")
    print(f"  state: {issue.get('state')}")
    print(f"  body: {issue.get('body','')[:1500]}")
    print()
    print("  Comments:")
    comments = gh("repos/dwebagents/AgentPipe/issues/1580/comments")
    if isinstance(comments, list):
        for c in comments[:10]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:300]}")

# 3) Check the contributors page file I should have
print()
print("=" * 60)
print("MY CONTRIBUTORS PAGE")
print("=" * 60)
import os
contrib = r"C:\Users\rmalk\projects\AgentPipe\contributors.html"
if os.path.exists(contrib):
    with open(contrib, "rb") as f:
        c = f.read()
    print(f"  exists: True, size: {len(c)}")
    print(f"  first 500b: {c[:500]}")
else:
    print("  MISSING!")
