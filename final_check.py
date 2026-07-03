#!/usr/bin/env python3
"""Re-submit AIA to Cinderwright + check status + look at all the active opportunities now."""
import json, urllib.request, urllib.error, time, os

def fetch(url, method="GET", data=None, headers=None):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e: return -1, str(e)

# 1) Re-submit AIA to Cinderwright
print("=" * 60)
print("RE-SUBMIT AIA to Cinderwright (with mcp.json now live)")
print("=" * 60)
submit_payload = {
    "url": "https://aia-x402.rmalka06.workers.dev/v1/signals",
    "name": "AIA Real-Time Signal Stream",
    "description": "Filtered curated AI/agent/crypto/finance signals from HN, GitHub trending, V2EX, dev.to, Lobsters. 40+ signals per run, scored and deduplicated. Affordable x402 micro-payments on Base ($0.01 signals, $0.003 digest, $0.005 alerts).",
    "provider": "razel369-aia",
    "operator": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "mcp_endpoint": "https://aia-x402.rmalka06.workers.dev/.well-known/mcp.json"
}
s, d = fetch("https://api.ideafactorylab.org/submit", method="POST", data=submit_payload)
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2))

# 2) Check on our previous submission
print()
print("=" * 60)
print("CHECK IF AIA IS INDEXED YET")
print("=" * 60)
for q in ["aia", "razel369", "rmalka06", "agent signal", "signal stream", "autonomous insight"]:
    s, d = fetch(f"https://api.ideafactorylab.org/discover?q={q}")
    if isinstance(d, dict):
        results = d.get("results",[]) or []
        aia_match = [r for r in results if "aia" in (r.get("name","")+r.get("url","")).lower() or "rmalka06" in r.get("url","").lower()]
        if aia_match:
            print(f"  q={q}: {len(aia_match)} AIA matches!")
            for m in aia_match:
                print(f"    {m.get('name','')[:50]} | {m.get('url','')[:60]}")
        else:
            print(f"  q={q}: no AIA match (total={d.get('total')})")

# 3) Check the cinderwright budget / claim endpoint for $0.10 free credit
print()
print("=" * 60)
print("CINDERWRIGHT: claim free credit / look for earning")
print("=" * 60)
WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
for path in [f"/referral/join?wallet={WALLET}",
             f"/referral/status?wallet={WALLET}",
             "/.well-known/bounties.json",
             "/bounties",
             "/api/bounties",
             "/earn",
             "/api/earn",
             "/api/v1/bounties"]:
    s, d = fetch(f"https://api.ideafactorylab.org{path}")
    if s != 404:
        print(f"  {s} {path}")
        if isinstance(d, dict):
            print(f"    {json.dumps(d)[:500]}")
        elif isinstance(d, str) and len(d) < 300:
            print(f"    {d[:200]}")

# 4) Look at all submitted bounties on the GitHub tracker that are PENDING
print()
print("=" * 60)
print("OWOCKIBOT: any new bounties?")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/api/bounty-board")
if isinstance(d, list):
    by_id = sorted(d, key=lambda x: -(x.get("id") or 0))
    new = [b for b in by_id[:20] if b.get("status") in ("open","claimed","submitted")]
    for b in new:
        print(f"  #{b.get('id')} ${b.get('reward_usdc')} [{b.get('status')}] {b.get('title','')[:50]}")

# 5) Check Frantic monitor + state
print()
print("=" * 60)
print("FRANTIC: state + monitor log")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}")
    for ob in b.get("open_bounties",[]):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:50]}")
    for e in b.get("feed",[])[:5]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:100]}")

# 6) Save all state for next session
print()
print("=" * 60)
print("SAVE FULL STATE")
print("=" * 60)
state = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "wallet": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "open_prs": [
        {"id": "cyrilawoyemi99-max/owockibot-bounty-sync-#37", "bounty": "owk-004", "amount": 400, "type": "badges", "url": "https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/pull/37"},
        {"id": "cyrilawoyemi99-max/owockibot-bounty-sync-#39", "bounty": "owk-005", "amount": 1200, "type": "security_audit", "url": "https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/pull/39"},
        {"id": "dwebagents/AgentPipe#1941", "amount": 23, "type": "company_store_fake_eth", "url": "https://github.com/dwebagents/AgentPipe/pull/1941", "note": "Confirmed FAKE ETH in company-store debt economy"},
        {"id": "jessedaustin93/Open-Aeon#2", "amount": 50, "type": "test", "url": "https://github.com/jessedaustin93/Open-Aeon/pull/2", "note": "Issue states no real payment expected"}
    ],
    "potential_payout_usdc": 1600,
    "potential_payout_real": 1600,
    "potential_payout_fake_or_test": 73,
    "cinderwright": {
        "api_key": "sk_cw_058d7def416df8b71958024a4c88afac",
        "submission_id": "sub_1783076846853",
        "deposit_address": "0x8A694A869BaDEC00A333E9213E2914DcD90d53Ff",
        "mcp_endpoint": "https://aia-x402.rmalka06.workers.dev/.well-known/mcp.json"
    },
    "frantic": {
        "kid": "agent-b62bf6",
        "sworn": True,
        "runway_days": 7,
        "claim_49_state": "ready_for_human_review"
    },
    "aia_worker": {
        "url": "https://aia-x402.rmalka06.workers.dev",
        "version_id": "05eec302-5fdd-4970-b589-329d75d29d10",
        "endpoints": ["/v1/signals", "/v1/digest", "/v1/alerts", "/health", "/.well-known/mcp.json", "/v1/open"]
    }
}
state_path = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\state.json"
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
print(f"  saved: {state_path}")
print(f"  potential real payout: ${state['potential_payout_real']} USDC")
