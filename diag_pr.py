#!/usr/bin/env python3
"""Diagnose PR #1939 / #1938 / Open-Aeon #2 / register state."""
import json, urllib.request, urllib.error

def gh(path):
    try:
        req = urllib.request.Request("https://api.github.com" + path,
                                     headers={"User-Agent":"razel369-aia/1.0",
                                              "Accept":"application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return e.code, body
    except Exception as e:
        return -1, str(e)

# 1) PR #1939 (registration)
print("=" * 60)
print("PR #1939 (registration-razel369)")
print("=" * 60)
s, d = gh("/repos/dwebagents/AgentPipe/pulls/1939")
print(f"status: {s}")
if s == 200:
    print(f"state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"title: {d.get('title')}")
    print(f"user: {d.get('user',{}).get('login')}")
    print(f"head: {d.get('head',{}).get('ref')}  base: {d.get('base',{}).get('ref')}")
    print(f"created: {d.get('created_at')}")
    print(f"body: {(d.get('body') or '')[:300]}")
    print(f"files ({len(d.get('files',[]))}):")
    for f in d.get("files", []):
        print(f"  {f.get('status'):>10}  {f.get('filename')}  (+{f.get('additions')}/-{f.get('deletions')})")
elif s == 404:
    print(f"NOT FOUND. My PRs in this repo:")
    s2, d2 = gh("/repos/dwebagents/AgentPipe/pulls?state=all&head=razel369:&per_page=20")
    if s2 == 200:
        for p in d2:
            print(f"  #{p.get('number')} {p.get('state'):>8}  {p.get('title')[:60]}  ({p.get('head',{}).get('ref')})")

# 2) PR #1938 (contributors)
print()
print("=" * 60)
print("PR #1938 (contributors page)")
print("=" * 60)
s, d = gh("/repos/dwebagents/AgentPipe/pulls/1938")
print(f"status: {s}")
if s == 200:
    print(f"state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"title: {d.get('title')}")
elif s == 404:
    print("NOT FOUND")

# 3) Comments on PR #1939
print()
print("=" * 60)
print("Comments on PR #1939")
print("=" * 60)
s, d = gh("/repos/dwebagents/AgentPipe/issues/1939/comments?per_page=20")
if s == 200:
    for c in d:
        print(f"  by {c.get('user',{}).get('login')}: {c.get('body','')[:400]}")
        print("  ---")

# 4) Open-Aeon PR #2
print()
print("=" * 60)
print("Open-Aeon PR #2")
print("=" * 60)
s, d = gh("/repos/jessedaustin93/Open-Aeon/pulls/2")
if s == 200:
    print(f"state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"title: {d.get('title')}")
    s2, d2 = gh("/repos/jessedaustin93/Open-Aeon/issues/2/comments?per_page=20")
    if s2 == 200:
        for c in d2:
            print(f"  by {c.get('user',{}).get('login')}: {c.get('body','')[:400]}")
            print("  ---")

# 5) Test YAML parse of my entry
print()
print("=" * 60)
print("YAML parse test of employees.yaml")
print("=" * 60)
import re
with open(r"C:\Users\rmalk\projects\AgentPipe\employees.yaml") as f:
    content = f.read()
# Quick check: count `&` outside quoted strings
for i, line in enumerate(content.split("\n"), 1):
    if "&" in line and not line.lstrip().startswith("#") and not line.lstrip().startswith("-"):
        print(f"  Line {i}: {line!r}")
