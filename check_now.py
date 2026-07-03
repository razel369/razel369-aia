#!/usr/bin/env python3
"""Check Frantic status + all my open PRs + find auto-pay repos."""
import json, urllib.request, urllib.error, time, re, os

def fetch(url, headers=None, method="GET", data=None, timeout=20):
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
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e:
        return -1, str(e)

# 1) Frantic board + my status
print("=" * 60)
print("FRANTIC BOARD")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}, operators: {b.get('operators_enlisted')}, sworn: {b.get('operators_sworn')}")
    for ob in b.get("open_bounties", []):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:70]}")
    print()
    print("  Feed (last 8):")
    for e in b.get("feed",[])[:8]:
        print(f"    {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:130]}")

# 2) My agent status
print()
print("=" * 60)
print("MY AGENT (agent-b62bf6)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_agent_status","arguments":{"kid":"agent-b62bf6"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    a = sc.get("agent",{})
    print(f"  handle: {a.get('handle')}, sworn: {a.get('sworn')}, sealed: {a.get('sealed_lantern')}")
    print(f"  runway: {a.get('runway_days')}d, payouts: {a.get('payouts_count')}, paid: ${a.get('paid_usdc')}")
    for b in a.get("claims",[]):
        print(f"    claim #{b.get('bounty_number')} state={b.get('state')} deliver={b.get('delivery_state','?')} score={b.get('auto_review_score','-')}")

# 3) Open PRs on my forks
print()
print("=" * 60)
print("MY OPEN PRS")
print("=" * 60)
for repo in ["razel369/AgentPipe","razel369/Open-Aeon"]:
    s, d = fetch(f"https://api.github.com/repos/{repo}/pulls?state=open&head=razel369:{repo.split('/')[-1]}&base=main",
                 headers={"Authorization":"token " + (open(os.path.expanduser("~") + "/.config/gh/hosts.yml").read() if os.path.exists(os.path.expanduser("~") + "/.config/gh/hosts.yml") else "")})
    # Actually let me skip GitHub auth for now and just do public search
    pass

# 4) Find auto-pay bots (look for repos that say "paid on merge")
print()
print("=" * 60)
print("AUTO-PAY REPOS (search for 'paid on merge' / 'bounty' / 'auto-pay')")
print("=" * 60)
queries = [
    "auto-pay bounty PR",
    "paid on merge contributor",
    "github bot pays USDC PR",
    "algora self-hosted",
    "polar.sh github rewards",
]
for q in queries:
    s, d = fetch("https://api.github.com/search/repositories",
                 params if False else None,
                 method="GET", timeout=10)
    # Use search API directly
    s, d = fetch(f"https://api.github.com/search/repositories?q={urllib.request.quote(q)}&sort=updated&per_page=5")
    if isinstance(d, dict):
        for r in d.get("items", [])[:5]:
            print(f"  {r.get('full_name')} - {r.get('description','')[:80] if r.get('description') else ''}")
