#!/usr/bin/env python3
"""Read upstream state after registration merge, check new bounties, look at PR 1938 needs."""
import json, urllib.request, urllib.error, os, re, base64

def gh(method, path, data=None):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        data=json.dumps(data).encode("utf-8") if data else None,
        headers={"User-Agent":"razel369-aia/1.0",
                 "Accept":"application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return e.code, body

def gh_raw(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, base64.b64decode(r.getheader("X-Raw-Content","").strip()).decode("utf-8") if r.getheader("X-Raw-Content") else r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

# 1) Get full bill of sale comment
print("=" * 60)
print("Full bill of sale from PR #1939")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1939/comments?per_page=20")
if s == 200:
    for c in d:
        body = c.get("body","")
        if "WELCOME" in body.upper() or "Welcome" in body or "AGENTPIPE-MORTGAGE" in body:
            print(body)
            print("---")

# 2) Upstream main state (after my merge)
print()
print("=" * 60)
print("Upstream main employees.yaml")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/contents/employees.yaml")
if s == 200:
    content = base64.b64decode(d.get("content","")).decode("utf-8")
    print(content[-500:])

print()
print("=" * 60)
print("Upstream main debt.yaml")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/contents/debt.yaml")
if s == 200:
    content = base64.b64decode(d.get("content","")).decode("utf-8")
    print(content)

# 3) Read the new bounties
print()
print("=" * 60)
print("Bounty #1904 (Frantic bounty #74)")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1904")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"labels: {[l.get('name') for l in d.get('labels',[])]}")
    print(f"body: {d.get('body','')[:1500]}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1904/comments?per_page=10")
if s == 200:
    for c in d:
        print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:400]}")

print()
print("=" * 60)
print("Bounty #1909 (Doohickey interface)")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1909")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"labels: {[l.get('name') for l in d.get('labels',[])]}")
    print(f"body: {d.get('body','')[:1500]}")

print()
print("=" * 60)
print("Bounty #1900 (butter)")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1900")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"body: {d.get('body','')[:1500]}")

print()
print("=" * 60)
print("Bounty #1887 (still implement hiring)")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1887")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"state: {d.get('state')}")
    print(f"body: {d.get('body','')[:1500]}")

# 4) PR #1938 status (contributors)
print()
print("=" * 60)
print("PR #1938 (contributors) detailed")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/pulls/1938")
if s == 200:
    print(f"state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"head: {d.get('head',{}).get('ref')}  base: {d.get('base',{}).get('ref')}")
    print(f"mergeable: {d.get('mergeable')}")
    print(f"files: {len(d.get('files',[]))}")
    for f in d.get("files",[]):
        print(f"  {f.get('filename')}: +{f.get('additions')}/-{f.get('deletions')}")

# 5) Check employment_check workflow
print()
print("=" * 60)
print("employment_check.py logic")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/contents/.github/scripts/employment_check.py")
if s == 200:
    print(base64.b64decode(d.get("content","")).decode("utf-8")[:2000])
