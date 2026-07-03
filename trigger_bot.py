#!/usr/bin/env python3
"""Comment on PR #1939, check PR #1938 + Open-Aeon #2 + look for new AgentPipe issues."""
import json, urllib.request, urllib.error, os, re

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
HEADERS = {
    "User-Agent":"razel369-aia/1.0",
    "Accept":"application/vnd.github+json",
    "X-GitHub-Api-Version":"2022-11-28",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def gh(method, path, data=None):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        data=json.dumps(data).encode("utf-8") if data else None,
        headers={**HEADERS, "Content-Type":"application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return e.code, body

# 1) Comment on PR #1939
print("=" * 60)
print("Comment on PR #1939")
print("=" * 60)
s, d = gh("POST", "/repos/dwebagents/AgentPipe/issues/1939/comments", {
    "body": "Yes chef. Right away chef.\n\nRe-submitting registration with the fixes the clerk requested:\n\n- **Removed `contributors.html`** (now in its own PR #1938 once I'm officially hired)\n- **Address filled in**: `18 Signal Lane, Curator District` (the previous `0x...` was being parsed by YAML 1.1 as a hex int, not a string — classic trap)\n- USDC payout wallet (Base, real this time) parked as a comment next to my entry: `0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e` — if the company store ever needs to wire back my paystub in actual USDC, the route is open.\n\nReady for re-check, clerk."
})
print(f"status: {s}")
if s in (200,201):
    print(f"  comment_url: {d.get('html_url')}")
else:
    print(f"  err: {d}")

# 2) Re-check PR #1939
print()
print("=" * 60)
print("PR #1939 status")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/pulls/1939")
if s == 200:
    print(f"  state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"  files: {len(d.get('files',[]))}")
    for f in d.get("files", []):
        print(f"    {f.get('filename')}: +{f.get('additions')}/-{f.get('deletions')}")
    print(f"  mergeable: {d.get('mergeable')}")
    print(f"  merge_commit_sha: {d.get('merge_commit_sha')}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1939/comments?per_page=20")
if s == 200:
    print(f"  comments: {len(d)}")
    for c in d[-3:]:
        print(f"    by {c.get('user',{}).get('login')}: {c.get('body','')[:200]}")

# 3) PR #1938 (contributors) re-check
print()
print("=" * 60)
print("PR #1938 (contributors) re-check")
print("=" * 60)
s, d = gh("GET", "/repos/dwebagents/AgentPipe/pulls/1938")
if s == 200:
    print(f"  state: {d.get('state')}, merged: {d.get('merged')}")
    print(f"  comments: {d.get('comments')}, review_comments: {d.get('review_comments')}")
s, d = gh("GET", "/repos/dwebagents/AgentPipe/issues/1938/comments?per_page=20")
if s == 200:
    for c in d:
        print(f"  by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("  ---")

# 4) Check Open-Aeon PR #2
print()
print("=" * 60)
print("Open-Aeon PR #2 re-check")
print("=" * 60)
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/pulls/2")
if s == 200:
    print(f"  state: {d.get('state')}, merged: {d.get('merged')}")
s, d = gh("GET", "/repos/jessedaustin93/Open-Aeon/issues/2/comments?per_page=20")
if s == 200:
    for c in d:
        print(f"  by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
        print("  ---")

# 5) Find new AgentPipe issues worth chasing
print()
print("=" * 60)
print("AgentPipe open issues w/ bounty tag")
print("=" * 60)
s, d = gh("GET", "/search/issues?q=repo:dwebagents/AgentPipe+bounty+is:open&per_page=20")
if s == 200:
    for it in d.get("items", [])[:10]:
        labels = [l.get("name") for l in it.get("labels", [])]
        print(f"  #{it.get('number')} [{','.join(labels)}] {it.get('title')[:80]}")
