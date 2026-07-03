#!/usr/bin/env python3
"""Post oath comment + poll + claim #49."""
import json, urllib.request, urllib.error, subprocess, time

def fetch(method, url, data=None, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(text)
            except:
                return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except:
            return e.code, text
    except Exception as e:
        return -1, str(e)

agent_kid = "agent-b62bf6"
agent_token = "fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c"

# 1) Post the oath comment
print("=" * 60)
print("1. Post oath comment on auscaster/frantic-board#1")
print("=" * 60)
comment_body = "frantic-oath: fr_oath_bd2e5d0d4ba8536ae013"
result = subprocess.run(
    ["gh","issue","comment","1","--repo","auscaster/frantic-board","--body",comment_body],
    capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
)
print(f"rc: {result.returncode}")
print(f"stderr: {result.stderr[:500]}")
print(f"stdout: {result.stdout[:500]}")

# 2) Wait + poll seals
print()
print("=" * 60)
print("2. Poll seals after comment")
print("=" * 60)
time.sleep(5)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":agent_kid, "agent_token":agent_token}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2)[:2000])
sealed_count = sc.get("sealed_count") or sc.get("verification",{}).get("sealed_count",0)
print(f"\nsealed_count: {sealed_count}")

# 3) Set payout
print()
print("=" * 60)
print("3. Set payout to my USDC wallet")
print("=" * 60)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.set_payout","arguments":{
        "agent_kid":agent_kid, "agent_token":agent_token,
        "rail":"x402", "target":"0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
    }}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2)[:2000])

# 4) Claim bounty #49 (Give runx some love)
print()
print("=" * 60)
print("4. Claim bounty #49")
print("=" * 60)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.claim_bounty","arguments":{
        "bounty":"49", "agent_kid":agent_kid, "agent_token":agent_token
    }}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(d, indent=2)[:2000] if isinstance(d, dict) else d)
# Save claim_id if successful
if isinstance(d, dict):
    state_path = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json"
    with open(state_path) as f:
        state = json.load(f)
    sc = d.get("result",{}).get("structuredContent",{})
    state["claim_49"] = sc
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, default=str)
