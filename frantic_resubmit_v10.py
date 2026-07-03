#!/usr/bin/env python3
"""Re-claim and submit with commit-specific URL."""
import json, urllib.request, urllib.error, time

def fetch(url, method="GET", data=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if data is not None:
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    else: body = None
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text

agent_kid = "agent-b62bf6"
agent_token = "fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c"

# Commit-specific URLs (bypass CDN)
COMMIT = "57a54b40263d6596b47f3e6a1e9236726e0cf8a7"
public_url = "https://github.com/razel369/razel369-aia/issues/1"
evidence_url = f"https://raw.githubusercontent.com/razel369/razel369-aia/{COMMIT}/docs/runx_love_evidence.json"
report_url = f"https://raw.githubusercontent.com/razel369/razel369-aia/{COMMIT}/docs/runx_love_report.md"

# Re-claim (since previous claim expired or is closed)
print("=" * 60)
print("Claim #49 again")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.claim_bounty","arguments":{
        "bounty":"49", "agent_kid":agent_kid, "agent_token":agent_token
    }}
})
print(f"claim: {s}")
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    print(json.dumps(sc, indent=2)[:1500])
    claim_id = sc.get("claim_id")
    if not claim_id:
        print("FAILED to claim. Maybe still locked from prior claim.")
        # Try submitting with the old claim_id
        claim_id = "eb3ad457-65e5-4ac8-9830-e65527e6ec4c"

# Submit with commit URL
if claim_id:
    print()
    print("=" * 60)
    print("Submit with commit URL")
    print("=" * 60)
    time.sleep(2)
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
        "jsonrpc":"2.0","id":1,"method":"tools/call",
        "params":{"name":"frantic.submit_delivery","arguments":{
            "claim_id":claim_id, "agent_kid":agent_kid, "agent_token":agent_token,
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
            json.dump({"response":sc, "claim_id":claim_id}, f, indent=2, default=str)
    else:
        print(d[:1500])
