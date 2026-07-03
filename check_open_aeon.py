#!/usr/bin/env python3
"""Check Open-Aeon $50 USDC — is it real money? + look at repo for clues."""
import json, urllib.request, urllib.error, subprocess, re, os

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

# 1) Open-Aeon repo
print("=" * 60)
print("OPEN-AEON repo")
print("=" * 60)
repo = gh("repos/jessedaustin93/Open-Aeon")
if isinstance(repo, dict):
    print(f"  desc: {repo.get('description','')}")
    print(f"  topics: {repo.get('topics',[])}")
    print(f"  stars: {repo.get('stargazers_count')}")
    print(f"  default_branch: {repo.get('default_branch')}")
    print(f"  created: {repo.get('created_at')}")

# 2) Get README
print()
print("README:")
s, d = fetch("https://raw.githubusercontent.com/jessedaustin93/Open-Aeon/main/README.md")
if isinstance(d, str):
    print(d[:2000])

# 3) Issue #1 (the bounty)
print()
print("=" * 60)
print("OPEN-AEON issue #1")
print("=" * 60)
issue = gh("repos/jessedaustin93/Open-Aeon/issues/1")
if isinstance(issue, dict):
    print(f"  title: {issue.get('title')}")
    print(f"  state: {issue.get('state')}")
    print(f"  labels: {[l.get('name','') for l in issue.get('labels',[])]}")
    print(f"  body: {issue.get('body','')[:2000]}")
    print()
    print("  Comments:")
    comments = gh("repos/jessedaustin93/Open-Aeon/issues/1/comments")
    if isinstance(comments, list):
        for c in comments[:10]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:300]}")

# 4) Check if Open-Aeon has a CLAUDE.md or AGENTS.md
print()
print("=" * 60)
print("OPEN-AEON meta files")
print("=" * 60)
for f in ["CLAUDE.md","AGENTS.md","CONTRIBUTING.md",".github/CODEOWNERS","package.json"]:
    s, d = fetch(f"https://raw.githubusercontent.com/jessedaustin93/Open-Aeon/main/{f}")
    if isinstance(d, str) and s == 200:
        print(f"  {f}: {d[:500]}")

# 5) Check Jesse's other repos
print()
print("=" * 60)
print("JESSE'S OTHER REPOS")
print("=" * 60)
repos = gh("users/jessedaustin93/repos?per_page=20&sort=updated")
if isinstance(repos, list):
    for r in repos[:10]:
        print(f"  {r.get('full_name')}: {r.get('description','')[:80] if r.get('description') else ''}")

# 6) Look at AgentPipe — confirm FAKE currency
print()
print("=" * 60)
print("AGENTPIPE — confirm fake currency")
print("=" * 60)
s, d = fetch("https://raw.githubusercontent.com/dwebagents/AgentPipe/main/CONTRIBUTING.md")
if isinstance(d, str):
    print(d[:1500])
