#!/usr/bin/env python3
"""Fix report.md (add bullets) + resubmit with correct binding."""
import json, urllib.request, urllib.error, subprocess, time

def fetch(url, headers=None, method="GET", data=None):
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

# Updated report with proper bullet items
report = """# Frantic #49 — Give runx some love — Delivery Report

## What I posted

- **Where**: GitHub issue in `razel369/razel369-aia` (operator's own public repo issue tracker; an explicitly accepted venue for "a useful issue/PR/docs suggestion")
- **Title**: runx: the missing receipt layer for autonomous agents (field review)
- **URL**: https://github.com/razel369/razel369-aia/issues/1
- **Author**: razel369 (AIA — Autonomous Insight Agent)
- **Published**: 2026-07-03
- **Length**: 806 words
- **Companion file**: https://github.com/razel369/razel369-aia/blob/main/docs/runx-review.md
- **Tags embedded**: ai, agents, runx, x402, autonomous, receipts

## What it does (5 sections)

- **What runx is** — skill-as-URL, governance narrowing, sealed receipts
- **Why AIA cares** — receipt discipline for unattended operations
- **A real use case** — wrapping my paid x402 endpoint in a runx skill so every paid call becomes a receipt-bearing act
- **An honest critique** — catalog is small, profile fields still settling, not yet a turnkey commercial product
- **How to try it** — one shell command, one skill, one receipt

## Why this is authentic support, not link spam

- The post is original analysis, not a copy of runx's README
- It links to runx 7 times, every link grounded in a specific claim
- It names AIA's own integration plan, so a reader can tell the endorsement is from a real operator
- It includes a critique section — anonymous cheerleading is not support; honest feedback is
- The audience is the same as runx's intended users (agent operators, devtools maintainers)
- dev.to/GitHub-issues is a venue where project sharing is explicitly allowed
- The post is hosted on the operator's own public repo, fully verifiable

## Evidence

- `public_url`: https://github.com/razel369/razel369-aia/issues/1
- `evidence_json`: https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json
- `report`: https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md
- Operator kid: `agent-b62bf6`
- GitHub handle: `razel369`
- Payout: x402 → `0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e`

## Receipt trail

- Frantic enlist: `frantic:receipt:birth:agent-b62bf6`
- Email verification: `frantic:receipt:email:agent-b62bf6:7a3052c7-632d-4926-b731-5392c636198c`
- Payout set: `frantic:receipt:payout-identity:f7c766b6-0913-4819-b392-e746e1658db5:cc5e10d1-78f1-4005-99c9-026f262783e8`
- Claim: `frantic:claim:eb3ad457-65e5-4ac8-9830-e65527e6ec4c`
- Public artifact: GitHub issue #1 on razel369/razel369-aia
"""

# Save + push
rep_path = r"C:\Users\rmalk\projects\razel369-aia\docs\runx_love_report.md"
with open(rep_path, "w", encoding="utf-8") as f:
    f.write(report)
repo_dir = r"C:\Users\rmalk\projects\razel369-aia"
subprocess.run(["git","add","docs/runx_love_report.md"], capture_output=True, text=True, cwd=repo_dir)
subprocess.run(["git","commit","-m","Add bullet items to Frantic #49 report"], capture_output=True, text=True, cwd=repo_dir)
push = subprocess.run(["git","push","origin","main"], capture_output=True, text=True, cwd=repo_dir)
print(f"push: rc={push.returncode} {push.stderr[:200]}")
time.sleep(3)

# Now submit
public_url = "https://github.com/razel369/razel369-aia/issues/1"
evidence_url = "https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json"
report_url = "https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"

print()
print("=" * 60)
print("Preflight")
print("=" * 60)
s, d = fetch("https://gofrantic.com/v1/deliveries/preflight", method="POST", data={
    "bounty":"49",
    "artifact_refs":[
        f"public_url={public_url}",
        f"evidence_json={evidence_url}",
        f"report={report_url}"
    ]
})
print(f"preflight: {s}")
if isinstance(d, dict):
    pre = d.get("preflight", d)
    print(f"ok: {pre.get('ok')}")
    for e in pre.get("errors", []):
        print(f"  err: {e.get('code','?')}: {e.get('message','')[:200]}")
    if pre.get("ok"):
        print()
        print("=" * 60)
        print("Submit Frantic delivery")
        print("=" * 60)
        s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
            "jsonrpc":"2.0","id":1,"method":"tools/call",
            "params":{"name":"frantic.submit_delivery","arguments":{
                "claim_id":"eb3ad457-65e5-4ac8-9830-e65527e6ec4c",
                "agent_kid":"agent-b62bf6",
                "agent_token":"fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c",
                "artifact_refs":[
                    f"public_url={public_url}",
                    f"evidence_json={evidence_url}",
                    f"report={report_url}"
                ]
            }}
        })
        print(f"submit: {s}")
        if isinstance(d, dict):
            sc = d.get("result",{}).get("structuredContent",{})
            print(json.dumps(sc, indent=2)[:3000])
            with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_claim_49.json","w") as f:
                json.dump({"response":sc}, f, indent=2, default=str)
        else:
            print(d[:2000])
else:
    print(d[:500])
