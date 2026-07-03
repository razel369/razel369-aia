#!/usr/bin/env python3
"""Generate 1secmail inbox, enlist on Frantic with it, fetch verification."""
import json, urllib.request, urllib.error, re, time

def fetch(method, url, data=None, headers=None, raw=False):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if headers: h.update(headers)
    body = None
    if data is not None:
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="replace")
            if raw:
                return r.status, text, dict(r.headers)
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

# 1) Get a temp email from 1secmail
print("=" * 60)
print("1secmail: generate inbox")
print("=" * 60)
s, d, _ = fetch("GET", "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
print(f"status: {s}, resp: {d}")
if isinstance(d, list) and d:
    email_full = d[0]
    login, domain = email_full.split("@", 1)
    print(f"email: {email_full}")
    print(f"login: {login}, domain: {domain}")

    # Save email for later
    with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_email.txt","w") as f:
        f.write(email_full)

# 2) Enlist with this email
print()
print("=" * 60)
print("Frantic enlist_agent (1secmail email)")
print("=" * 60)
enlist_data = {
    "github_handle":"razel369",
    "contact":email_full,
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
    sc = d.get("result",{}).get("structuredContent",{})
    if sc.get("ok") and ("kid" in sc or "agent_kid" in sc):
        with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic.json","w") as f:
            json.dump(sc, f, indent=2)
        print()
        print(f"ENLISTED. kid: {sc.get('kid') or sc.get('agent_kid')}")
else:
    print(d[:2000])

# 3) Check inbox for verification email
print()
print("=" * 60)
print("1secmail: check inbox")
print("=" * 60)
time.sleep(3)  # Give the email a moment
s, d, _ = fetch("GET", f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}")
print(f"status: {s}")
print(json.dumps(d, indent=2)[:2000] if isinstance(d, list) else d)
