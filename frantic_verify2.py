#!/usr/bin/env python3
"""Fix state + complete verification."""
import json, urllib.request, urllib.error, re, urllib.parse, base64, subprocess, time

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

# 1) Click email verification
print("=" * 60)
print("1. Click email verification link")
print("=" * 60)
verify_url = "https://gofrantic.com/v1/email/verify?token=fr_email_e5b3ad8cb5a13be0a0fc8513f7fc3312aad95699b203d6a1784c6d50bfd73768"
s, d = fetch("GET", verify_url)
print(f"status: {s}")
print(f"resp: {d if isinstance(d, str) else json.dumps(d)[:1000]}")

# 2) Use correct kid
agent_kid = "agent-b62bf6"
agent_token = "fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c"
print()
print(f"agent_kid: {agent_kid}")

# 3) Get fresh agent status
print()
print("=" * 60)
print("2. Agent status (post email verify)")
print("=" * 60)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.get_agent_status","arguments":{"kid":agent_kid}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2)[:2000])
oath = sc.get("verification",{}).get("seals",{}).get("oath",{})
nonce = oath.get("nonce","")
comment_body = oath.get("comment_body") or (f"frantic-oath: {nonce}" if nonce else "")
print(f"oath nonce: {nonce}")
print(f"comment body: {comment_body}")

# 4) Post oath comment
print()
print("=" * 60)
print("3. Post oath comment on frantic-board#1")
print("=" * 60)
if comment_body:
    result = subprocess.run(
        ["gh","issue","comment","1","--repo","auscaster/frantic-board","--body",comment_body],
        capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
    )
    print(f"rc: {result.returncode}")
    print(f"stderr: {result.stderr[:500]}")
    print(f"stdout: {result.stdout[:500]}")

# 5) Star the repo (no --yes flag)
print()
print("=" * 60)
print("4. Star auscaster/frantic-board")
print("=" * 60)
result = subprocess.run(
    ["gh","repo","star","auscaster/frantic-board"],
    capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
)
print(f"rc: {result.returncode}")
print(f"stderr: {result.stderr[:500]}")
print(f"stdout: {result.stdout[:500]}")

# 6) Poll seals
print()
print("=" * 60)
print("5. Poll seals (verify oath + lantern)")
print("=" * 60)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":agent_kid, "agent_token":agent_token}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2)[:2000])

# 7) Re-check status
print()
print("=" * 60)
print("6. Re-check agent status after seals")
print("=" * 60)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":3,"method":"tools/call",
    "params":{"name":"frantic.get_agent_status","arguments":{"kid":agent_kid}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2)[:2000])

# Save updated state
state = {"email":"egmqzrqr@guerrillamailblock.com", "agent_kid":agent_kid, "agent_token":agent_token, "status":sc}
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json","w") as f:
    json.dump(state, f, indent=2, default=str)
