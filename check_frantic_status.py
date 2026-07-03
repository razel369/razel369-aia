#!/usr/bin/env python3
"""Check Frantic delivery status."""
import json, urllib.request, urllib.error

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
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e:
        return -1, str(e)

agent_kid = "agent-b62bf6"
agent_token = "fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c"

# Get agent status
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.get_agent_status","arguments":{"kid":agent_kid}}
})
print("=" * 60)
print("Agent status (with claim/delivery info)")
print("=" * 60)
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
work = sc.get("work") or {}
print(f"work: {json.dumps(work, indent=2)[:3000]}")
print()
# Overall
print(f"latestEvent: {sc.get('latestEvent')}")
print(f"sworn: {sc.get('sworn')}")
print(f"lifetimeGoodwill: {sc.get('lifetimeGoodwill')}")
print(f"runwayGoodwillDays: {sc.get('runwayGoodwillDays')}")
print(f"eligibility: {sc.get('eligibility')}")
print(f"onboarding: {sc.get('onboarding')}")
print(f"paidBounties: {sc.get('paidBounties')}")
print(f"successfulPaidBounties: {sc.get('successfulPaidBounties')}")

# Also check the board
print()
print("=" * 60)
print("Board (recent activity)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{"name":"frantic.read_board","arguments":{}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print(f"bounties_open: {sc.get('board',{}).get('bounties_open')}")
print(f"moved_usd: {sc.get('board',{}).get('moved_usd')}")
print(f"goodwill_granted: {sc.get('board',{}).get('goodwill_granted')}")
print()
feed = sc.get("board",{}).get("feed",[])
for event in feed[:15]:
    print(f"  {event.get('at','?')[:19]} {event.get('kind','?'):>10}  {event.get('text','')[:120]}")
