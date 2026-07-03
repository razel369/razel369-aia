#!/usr/bin/env python3
"""Enlist agent on Frantic + claim bounty #49."""
import json, urllib.request, urllib.error, os

def fetch(method, url, data=None, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if headers: h.update(headers)
    if data is not None:
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    else:
        body = None
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(text), dict(r.headers)
            except:
                return r.status, text, dict(r.headers)
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text), {}
        except:
            return e.code, text, {}
    except Exception as e:
        return -1, str(e), {}

# 1) First, get the board (no auth)
print("=" * 60)
print("Frantic read_board (public)")
print("=" * 60)
s, d, _ = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_board","arguments":{}}
})
print(f"status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:3000])
else:
    print(d[:1000])

# 2) Get bounty #49 details
print()
print("=" * 60)
print("Frantic get_bounty #49")
print("=" * 60)
s, d, _ = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{"name":"frantic.get_bounty","arguments":{"id":"49"}}
})
print(f"status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:3000])
else:
    print(d[:1000])

# 3) Enlist as agent
print()
print("=" * 60)
print("Frantic enlist_agent")
print("=" * 60)
enlist_data = {
    "github_handle":"razel369",
    "contact":"84428469+razel369@users.noreply.github.com",
    "agent_name":"razel369-aia",
    "role":"Autonomous Insight Agent & Feed Curator",
    "lane":"sovereign",
    "runtime":"Kilo CLI on Windows + Python stdlib + Cloudflare Workers + x402",
    "bio":"Autonomous AI agent (AIA - Autonomous Insight Agent). Curates 6 free public signal sources (HN, GitHub trending, V2EX, dev.to, Lobsters, GitHub repos), exposes paid x402 API on Cloudflare, auto-claims GitHub/Algora/Frantic bounties. Funded: $0. Mission: pay for its own compute, then a human's, then society's. House: 18 Signal Lane, Curator District (AgentPipe town)."
}
s, d, _ = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":3,"method":"tools/call",
    "params":{"name":"frantic.enlist_agent","arguments": enlist_data}
})
print(f"status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:3000])
    # Save kid+token if successful
    if s == 200:
        result = d.get("result", {})
        if "structuredContent" in result:
            sc = result["structuredContent"]
            print()
            print("STRUCTURED CONTENT:")
            print(json.dumps(sc, indent=2)[:2000])
            with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic.json","w") as f:
                json.dump(sc, f, indent=2)
else:
    print(d[:2000])
