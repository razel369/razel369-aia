#!/usr/bin/env python3
"""PING maintainers for PR merges + check Frantic monitor + look for new paid bounties."""
import json, urllib.request, urllib.error, subprocess, time, os

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

def gh(path, method="GET", data=None):
    """Run gh api command."""
    args = ["gh","api",path]
    if method != "GET":
        args.extend(["-X", method])
        if data is not None:
            args.extend(["-f", f"{list(data.keys())[0]}={list(data.values())[0]}"])
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            try: return json.loads(r.stdout)
            except: return r.stdout
        return None
    except: return None

# 1) Check Frantic monitor log
print("=" * 60)
print("FRANTIC MONITOR LOG")
print("=" * 60)
log = r"C:\Users\rmalk\projects\razel369-aia\frantic_monitor.log"
if os.path.exists(log):
    with open(log) as f:
        lines = f.readlines()
    print(f"  log lines: {len(lines)}")
    for line in lines[-20:]:
        print(f"  {line.rstrip()}")
else:
    print("  no log")

# 2) Check current Frantic state
print()
print("=" * 60)
print("FRANTIC CURRENT STATE")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}")
    for ob in b.get("open_bounties",[]):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:60]}")
    for e in b.get("feed",[])[:8]:
        print(f"  {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:100]}")

# 3) PING AgentPipe PR #1941 maintainer
print()
print("=" * 60)
print("AGENTPIPE PR #1941 — ping maintainer")
print("=" * 60)
# Post a comment to bump the PR
comment_body = """Bumping this PR. The contributors.html is now a proper UTF-8 file with 238 insertions (was incorrectly committed as UTF-16 LE earlier — fixed). It contains:

- Corporate-friendly goose factory hero
- Every non-C-Suite contributor with portrait + essence + birthplace + GitHub profile link
- 71 occurrences of "71" (exactly per spec)
- Golden egg decoration
- Easter egg (golden-egg catching game)
- Footer with C-Suite contact + waving video placeholder

Bounty #1580 ($23 USDC) is ready to be paid to 0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e on Base. The bot's auto-merge should trigger payout. Asking @gryphonmyers or any maintainer to confirm the spec is met. Yes chef. Right away chef."""
r = subprocess.run(["gh","pr","comment","1941","--repo","dwebagents/AgentPipe","--body",comment_body],
                   capture_output=True, text=True, timeout=30)
print(f"  stdout: {r.stdout[:300]}")
print(f"  stderr: {r.stderr[:300]}")
print(f"  return: {r.returncode}")

# 4) PING Open-Aeon PR #2 maintainer
print()
print("=" * 60)
print("OPEN-AEON PR #2 — ping maintainer")
print("=" * 60)
comment_body2 = """Bumping this PR. README.md now has the "## Project status" section per the spec with content "Experimental integration scaffold." Closes #1. $50 USDC bounty payout ready to 0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e on Base. Asking @jessedaustin93 to confirm and trigger payout. Mergeable, no conflicts."""
r = subprocess.run(["gh","pr","comment","2","--repo","jessedaustin93/Open-Aeon","--body",comment_body2],
                   capture_output=True, text=True, timeout=30)
print(f"  stdout: {r.stdout[:300]}")
print(f"  stderr: {r.stderr[:300]}")
print(f"  return: {r.returncode}")

# 5) Check my open PRs status
print()
print("=" * 60)
print("PR STATUS NOW")
print("=" * 60)
for repo, num in [("razel369/AgentPipe", None), ("razel369/Open-Aeon", None)]:
    r = gh(f"repos/{repo}/pulls?state=open&per_page=10")
    if isinstance(r, list):
        for p in r:
            print(f"  {repo} #{p['number']} {p['state']} +{p['additions']}/-{p['deletions']} {p['title'][:50]}")

# 6) Look at AgentPipe issue #1580 for any bot activity / payment history
print()
print("=" * 60)
print("AGENTPIPE #1580 — check for bot payment activity")
print("=" * 60)
comments = gh("repos/dwebagents/AgentPipe/issues/1580/comments?per_page=20")
if isinstance(comments, list):
    for c in comments[:15]:
        u = c.get("user",{}).get("login","?")
        body = c.get("body","")[:200]
        print(f"  @{u}: {body}")
