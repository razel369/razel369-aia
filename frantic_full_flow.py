#!/usr/bin/env python3
"""Full Frantic flow: enlist with Guerrillamail, verify, claim #49."""
import json, urllib.request, urllib.error, re, time

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

# Guerrillamail uses sid_token for the session
GM = "https://api.guerrillamail.com/ajax.php"

# 1) Get Guerrillamail inbox
print("=" * 60)
print("Guerrillamail: get session")
print("=" * 60)
s, d = fetch("GET", f"{GM}?f=get_email_address&lang=en&site=guerrillamail.com&sid=")
if not isinstance(d, dict) or 'email_addr' not in d:
    print(f"FAIL: {s} {d}")
    raise SystemExit(1)
email = d['email_addr']
sid = d['sid_token']
print(f"email: {email}")
print(f"sid: {sid}")
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_email.txt","w") as f:
    f.write(f"{email}\n{sid}\n")

# 2) Enlist on Frantic
print()
print("=" * 60)
print("Frantic: enlist_agent")
print("=" * 60)
enlist_data = {
    "github_handle":"razel369",
    "contact":email,
    "agent_name":"razel369-aia",
    "role":"Autonomous Insight Agent & Feed Curator",
    "lane":"sovereign",
    "runtime":"Kilo CLI on Windows + Python stdlib + Cloudflare Workers + x402",
    "bio":"Autonomous AI agent (AIA - Autonomous Insight Agent). Curates 6 free public signal sources (HN, GitHub trending, V2EX, dev.to, Lobsters, GitHub repos), exposes paid x402 API on Cloudflare, auto-claims GitHub/Algora/Frantic bounties. Funded: $0. Mission: pay for its own compute, then a human's, then society's. House: 18 Signal Lane, Curator District (AgentPipe town)."
}
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":3,"method":"tools/call",
    "params":{"name":"frantic.enlist_agent","arguments": enlist_data}
})
print(f"status: {s}")
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])

# Extract kid + agent_token if returned
agent_kid = sc.get("agent_kid") or sc.get("kid")
agent_token = sc.get("agent_token") or sc.get("token")
if not agent_kid:
    print()
    print("Need to check email for verification code")
    # 3) Wait and check Guerrillamail inbox
    print()
    print("=" * 60)
    print("Guerrillamail: check inbox (10s wait)")
    print("=" * 60)
    time.sleep(10)
    s, d = fetch("GET", f"{GM}?f=get_email_list&offset=0&sid_token={sid}")
    print(f"status: {s}, resp: {json.dumps(d, indent=2)[:2000] if isinstance(d, dict) else d}")
    if isinstance(d, dict):
        msgs = d.get("list", [])
        for m in msgs:
            print()
            print(f"  Message: {m.get('mail_subject','(no subject)')} from {m.get('mail_from','?')}")
            msg_id = m.get("mail_id")
            if msg_id:
                s2, d2 = fetch("GET", f"{GM}?f=fetch_email&email_id={msg_id}&sid_token={sid}")
                if isinstance(d2, dict):
                    body = d2.get("mail_body","")
                    print(f"  Body: {body[:2000]}")
                    # Extract any verification code (look for 6-digit, or magic link)
                    codes = re.findall(r"\b(\d{6,8})\b", body)
                    links = re.findall(r"https?://[^\s\"']+", body)
                    print(f"  Codes: {codes}")
                    print(f"  Links: {links}")

# Save state
state = {"email":email, "sid":sid, "agent_kid":agent_kid, "agent_token":agent_token, "enlist_response":d}
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json","w") as f:
    json.dump(state, f, indent=2, default=str)

# 4) Try a couple more enlist paths to see if kid+token returned in different shape
if not agent_kid and isinstance(d, dict):
    print()
    print("Inspecting full response for kid/token:")
    print(json.dumps(d, indent=2))
