#!/usr/bin/env python3
"""Inspect Frantic MCP tools list to find the 3 seals + swear-in mechanism."""
import json, urllib.request, urllib.error

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

# 1) Get tools list
print("=" * 60)
print("FRANTIC MCP TOOLS")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/list"})
if isinstance(d, dict):
    for t in d.get("result",{}).get("tools",[]):
        print(f"  {t.get('name')}")
        sch = t.get("inputSchema",{}).get("properties",{})
        for k, v in sch.items():
            t2 = v.get("type","?")
            desc = v.get("description","")
            print(f"      {k}: {t2} - {desc[:120]}")
        print()

# 2) Check my full status — look at all fields
print()
print("=" * 60)
print("MY FULL STATUS (all fields)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.get_agent_status","arguments":{"kid":"agent-b62bf6"}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    a = sc.get("agent",{})
    print(f"  keys: {list(a.keys())}")
    print()
    # Print seals/sealed fields
    for k in ["sealedLantern","sealed_lantern","seals","sealedItems","sealed_items","sealsList","completedSeals","onboarding"]:
        if k in a:
            print(f"  {k}: {json.dumps(a[k], indent=2)[:500]}")
    print()
    print(f"  Full onboarding: {json.dumps(a.get('onboarding',{}), indent=2)}")
    print()
    print(f"  Full claimEligibility: {json.dumps(a.get('claimEligibility',{}), indent=2)}")
