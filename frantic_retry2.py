#!/usr/bin/env python3
"""Retry Frantic + check agentic.market for AIA + check bounties."""
import json, urllib.request, urllib.error, time, urllib.parse

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

# 1) Frantic preflight
print("=" * 60)
print("Frantic preflight (post rate limit)")
print("=" * 60)
s, d = fetch("https://gofrantic.com/v1/deliveries/preflight", method="POST", data={
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print(f"status: {s}")
if isinstance(d, dict):
    pre = d.get("preflight", d)
    print(f"ok: {pre.get('ok')}")
    for e in pre.get("errors", []):
        print(f"  err: {e.get('code','?')}: {e.get('message','')[:200]}")
    if pre.get("ok"):
        print()
        print("Submitting...")
        agent_kid = "agent-b62bf6"
        agent_token = "fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c"
        claim_id = "eb3ad457-65e5-4ac8-9830-e65527e6ec4c"
        s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
            "jsonrpc":"2.0","id":1,"method":"tools/call",
            "params":{"name":"frantic.submit_delivery","arguments":{
                "claim_id":claim_id, "agent_kid":agent_kid, "agent_token":agent_token,
                "artifact_refs":[
                    f"public_url=https://github.com/razel369/razel369-aia/issues/1",
                    f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json",
                    f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
                ]
            }}
        })
        print(f"submit: {s}")
        if isinstance(d, dict):
            sc = d.get("result",{}).get("structuredContent",{})
            print(json.dumps(sc, indent=2)[:3000])
            with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_claim_49.json","w") as f:
                json.dump({"claim_id":claim_id, "response":sc}, f, indent=2, default=str)
        else:
            print(d[:2000])
else:
    print(d[:500])

# 2) Check agentic.market for AIA (might be indexed now after deploy)
print()
print("=" * 60)
print("agentic.market - search AIA after Worker deploy")
print("=" * 60)
time.sleep(2)
s, d = fetch("https://api.agentic.market/v1/services/search?q=aia")
if s == 200:
    services = d.get("services", [])
    print(f"aia: {len(services)} results")
    for sv in services[:5]:
        print(f"  {sv.get('name')} (${sv.get('priceSummary',{}).get('minAmount','?')}/call) — {sv.get('domain','')}")
s, d = fetch("https://api.agentic.market/v1/services/search?q=rmalka06")
if s == 200:
    print(f"rmalka06: {len(d.get('services',[]))} results")
s, d = fetch("https://api.agentic.market/v1/services/search?q=razel369")
if s == 200:
    print(f"razel369: {len(d.get('services',[]))} results")
s, d = fetch("https://api.agentic.market/v1/services/search?q=signal+stream")
if s == 200:
    print(f"signal stream: {len(d.get('services',[]))} results")
    for sv in d.get('services',[])[:3]:
        print(f"  {sv.get('name')}: {sv.get('description','')[:80]}")
