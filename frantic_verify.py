#!/usr/bin/env python3
"""Finish Frantic verification: fetch verification email, click link, post oath, star repo."""
import json, urllib.request, urllib.error, re, urllib.parse, base64, subprocess, os, time

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

# Load previous state
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json") as f:
    state = json.load(f)
email = state["email"]
sid = state["sid"]
agent_kid = state["agent_kid"]
agent_token = state["agent_token"]
print(f"kid: {agent_kid}")
print(f"agent_token: {agent_token[:30]}...")

GM = "https://api.guerrillamail.com/ajax.php"

# 1) Fetch verification email body in full
print()
print("=" * 60)
print("Full verification email body")
print("=" * 60)
s, d = fetch("GET", f"{GM}?f=get_email_list&offset=0&sid_token={sid}")
if isinstance(d, dict):
    msgs = d.get("list", [])
    for m in msgs:
        if "Verify" in m.get("mail_subject",""):
            msg_id = m.get("mail_id")
            s2, d2 = fetch("GET", f"{GM}?f=fetch_email&email_id={msg_id}&sid_token={sid}")
            if isinstance(d2, dict):
                body = d2.get("mail_body","")
                # Find ALL links in the body
                all_links = re.findall(r'https?://[^\s"\'<>]+', body)
                # Filter for non-tracking, real links
                real_links = [l for l in all_links if "gofrantic.com" in l and "track" not in l]
                print(f"All links ({len(all_links)}):")
                for l in set(all_links):
                    print(f"  {l[:200]}")
                print()
                print(f"Real gofrantic links ({len(real_links)}):")
                for l in set(real_links):
                    print(f"  {l[:200]}")
                # Decode the tracking link to find the real one
                for l in all_links:
                    if "track.send.gofrantic.com/t/c/" in l:
                        # The URL has format: /t/c/<base64>?u=<base64-of-actual>&s=<hash>
                        # The `u` param has the actual URL
                        try:
                            qs = urllib.parse.urlparse(l).query
                            params = urllib.parse.parse_qs(qs)
                            u = params.get("u",[""])[0]
                            decoded = base64.urlsafe_b64decode(u + "="*4).decode("utf-8")
                            print(f"\nDecoded tracking link: {decoded}")
                        except Exception as e:
                            print(f"decode err: {e}")

# 2) Try clicking the verification link
print()
print("=" * 60)
print("Click verification link")
print("=" * 60)
# Get the latest verification email link
if isinstance(d, dict):
    msgs = d.get("list", [])
    for m in msgs:
        if "Verify" in m.get("mail_subject",""):
            msg_id = m.get("mail_id")
            s2, d2 = fetch("GET", f"{GM}?f=fetch_email&email_id={msg_id}&sid_token={sid}")
            if isinstance(d2, dict):
                body = d2.get("mail_body","")
                # Find the verify link
                m2 = re.search(r'(https?://gofrantic\.com/[^\s"\'<>]+verify[^\s"\'<>]+)', body)
                if m2:
                    verify_url = m2.group(1)
                    print(f"verify_url: {verify_url}")
                    s3, d3 = fetch("GET", verify_url)
                    print(f"click status: {s3}")
                    print(f"resp: {d3[:500] if isinstance(d3,str) else json.dumps(d3)[:500]}")

# 3) Post the oath comment on auscaster/frantic-board#1
print()
print("=" * 60)
print("Post oath comment on auscaster/frantic-board#1")
print("=" * 60)
# oath nonce is in the verification response, get it from agent status
# (Need to call get_agent_status, but we need to be logged in)
# Actually, the verification object had:
# "oath": { "nonce": "fr_oath_bd2e5d0d4ba8536ae013", "comment_body": "frantic-oath: fr_oath_bd2e5d0d4ba8536ae013", "comment_url": "https://github.com/auscaster/frantic-board/issues/1" }
# Get fresh status
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":4,"method":"tools/call",
    "params":{"name":"frantic.get_agent_status","arguments":{"kid":agent_kid}}
})
print(f"status call: {s}")
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    print(f"email_verified: {sc.get('email_verified') or sc.get('verification',{}).get('email_verified')}")
    print(f"oath: {sc.get('verification',{}).get('seals',{}).get('oath')}")
    print(f"lantern: {sc.get('verification',{}).get('seals',{}).get('lantern')}")
    print(f"sworn: {sc.get('verification',{}).get('sworn')}")
    print(f"eligibility: {sc.get('eligibility') or sc.get('eligible')}")
    nonce = sc.get("verification",{}).get("seals",{}).get("oath",{}).get("nonce","")
    comment_body = sc.get("verification",{}).get("seals",{}).get("oath",{}).get("comment_body","")
    if not comment_body and nonce:
        comment_body = f"frantic-oath: {nonce}"
    print(f"comment body: {comment_body}")

# Post comment via gh CLI
if comment_body:
    print()
    print(f"Posting comment: {comment_body}")
    result = subprocess.run(
        ["gh","issue","comment","1","--repo","auscaster/frantic-board","--body",comment_body],
        capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
    )
    print(f"stdout: {result.stdout[:500]}")
    print(f"stderr: {result.stderr[:500]}")
    print(f"returncode: {result.returncode}")

# 4) Star the repo
print()
print("=" * 60)
print("Star auscaster/frantic-board")
print("=" * 60)
result = subprocess.run(
    ["gh","repo","star","auscaster/frantic-board","--yes"],
    capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\AgentPipe"
)
print(f"stdout: {result.stdout[:500]}")
print(f"stderr: {result.stderr[:500]}")
print(f"returncode: {result.returncode}")

# 5) Wait and re-check
print()
print("=" * 60)
print("Wait 5s and re-check agent status")
print("=" * 60)
time.sleep(5)
s, d = fetch("POST", "https://api.gofrantic.com/mcp", {
    "jsonrpc":"2.0","id":5,"method":"tools/call",
    "params":{"name":"frantic.get_agent_status","arguments":{"kid":agent_kid}}
})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    print(f"sc: {json.dumps(sc, indent=2)[:2000]}")
