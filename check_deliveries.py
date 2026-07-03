#!/usr/bin/env python3
"""Check #49 delivery feedback + Open-Aeon/AgentPipe PRs + my claim state."""
import json, urllib.request, urllib.error, os

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

# Load my token
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json") as f:
    raw = f.read()
    if raw[:3] == "\ufeff":
        raw = raw[3:]
    st = json.loads(raw)
KID = st.get("agent_kid")
TOKEN = st.get("agent_token")
print(f"kid: {KID}, token: {TOKEN[:20]}...")

# 1) Get #49 full
print()
print("=" * 60)
print("FRANTIC #49 (my delivery)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_bounty","arguments":{"id":"49"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
    print(json.dumps(b, indent=2)[:5000])

# 2) Open-Aeon PR #2 status (via gh CLI)
print()
print("=" * 60)
print("OPEN-AEON PR #2 (50 USDC)")
print("=" * 60)
import subprocess
try:
    r = subprocess.run(["gh","pr","list","--repo","razel369/Open-Aeon","--state","all","--json","number,title,state,mergeCommit,url"],
                       capture_output=True, text=True, timeout=30)
    print(f"  stdout: {r.stdout[:500]}")
    print(f"  stderr: {r.stderr[:200]}")
except Exception as e:
    print(f"  err: {e}")

# 3) AgentPipe PR #1941 status
print()
print("=" * 60)
print("AGENTPIPE PR #1941 (23 USDC)")
print("=" * 60)
try:
    r = subprocess.run(["gh","pr","list","--repo","razel369/AgentPipe","--state","all","--json","number,title,state,mergeCommit,url"],
                       capture_output=True, text=True, timeout=30)
    print(f"  stdout: {r.stdout[:500]}")
    print(f"  stderr: {r.stderr[:200]}")
except Exception as e:
    print(f"  err: {e}")

# 4) Try to see my claim state
print()
print("=" * 60)
print("MY CLAIM STATE")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":KID,"agent_token":TOKEN}}})
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])

# 5) Try to see if there's a 'list_bounties' or 'open_bounties' method
print()
print("=" * 60)
print("MCP TOOLS DETAIL")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/list"})
if isinstance(d, dict):
    for t in d.get("result",{}).get("tools",[]):
        sch = t.get("inputSchema",{})
        print(f"  {t.get('name')}: {json.dumps(sch)[:300]}")
