#!/usr/bin/env python3
"""Find oath nonce + star via API + post comment + poll seals."""
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

# 1) Get full status - extract oath nonce
print("=" * 60)
print("1. Full agent status (find oath nonce)")
print("=" * 60)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.get_agent_status","arguments":{"kid":agent_kid}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2))

# Look in different places
import re
content = json.dumps(sc)
nonces = re.findall(r"fr_oath_[a-f0-9]+", content)
print(f"nonces found: {nonces}")
# Also look for any "comment_body" field
bodies = re.findall(r"comment_body[\"']?\s*[:=]\s*[\"']([^\"']+)[\"']", content)
print(f"comment_bodies: {bodies}")

# 2) If we have a nonce, post the comment
print()
print("=" * 60)
print("2. Post oath comment")
print("=" * 60)
# If no nonce, we may need to call a specific endpoint
if not nonces:
    # Try the signup again or call poll_seals to see what's needed
    s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
        "jsonrpc":"2.0","id":1,"method":"tools/call",
        "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":agent_kid, "agent_token":agent_token}}
    })
    print(json.dumps(d, indent=2)[:2000])
else:
    nonce = nonces[0]
    body_text = f"frantic-oath: {nonce}"
    print(f"posting: {body_text}")
    result = subprocess.run(
        ["gh","issue","comment","1","--repo","auscaster/frantic-board","--body",body_text],
        capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
    )
    print(f"rc: {result.returncode}")
    print(f"stderr: {result.stderr[:500]}")
    print(f"stdout: {result.stdout[:500]}")

# 3) Star the repo via API (PUT /user/starred/{owner}/{repo})
print()
print("=" * 60)
print("3. Star auscaster/frantic-board via GitHub API")
print("=" * 60)
# Use gh api
result = subprocess.run(
    ["gh","api","-X","PUT","/user/starred/auscaster/frantic-board"],
    capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
)
print(f"rc: {result.returncode}")
print(f"stderr: {result.stderr[:500]}")
print(f"stdout: {result.stdout[:500]}")

# 4) Also star runxhq/runx
print()
print("=" * 60)
print("4. Star runxhq/runx via GitHub API")
print("=" * 60)
result = subprocess.run(
    ["gh","api","-X","PUT","/user/starred/runxhq/runx"],
    capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
)
print(f"rc: {result.returncode}")
print(f"stderr: {result.stderr[:500]}")
print(f"stdout: {result.stdout[:500]}")

# 5) Wait 5s and poll seals
print()
print("=" * 60)
print("5. Wait and poll seals")
print("=" * 60)
time.sleep(5)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{"name":"frantic.poll_seals","arguments":{"agent_kid":agent_kid, "agent_token":agent_token}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(json.dumps(sc, indent=2)[:2000])
