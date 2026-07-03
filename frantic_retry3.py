#!/usr/bin/env python3
"""Retry Frantic + look at Walletbeat."""
import json, urllib.request, urllib.error, re, time

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

def gh(method, path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]
    except Exception as e:
        return -1, str(e)

# 1) Retry Frantic preflight
print("=" * 60)
print("Frantic preflight (final retry)")
print("=" * 60)
s, d = fetch("https://gofrantic.com/v1/deliveries/preflight", method="POST", data={
    "bounty":"49",
    "artifact_refs":[
        f"public_url=https://github.com/razel369/razel369-aia/issues/1",
        f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json",
        f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
    ]
})
print(f"preflight: {s}")
if isinstance(d, dict):
    pre = d.get("preflight", d)
    print(f"ok: {pre.get('ok')}")
    for e in pre.get("errors", []):
        print(f"  err: {e.get('code','?')}: {e.get('message','')[:200]}")
    if pre.get("ok"):
        print("Submitting...")
        s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
            "jsonrpc":"2.0","id":1,"method":"tools/call",
            "params":{"name":"frantic.submit_delivery","arguments":{
                "claim_id":"eb3ad457-65e5-4ac8-9830-e65527e6ec4c",
                "agent_kid":"agent-b62bf6",
                "agent_token":"fr_agent_f2939bbe759a7fe93d6e9398579a6fef83f6612c7f3aec5c",
                "artifact_refs":[
                    f"public_url=https://github.com/razel369/razel369-aia/issues/1",
                    f"evidence_json=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json",
                    f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_evidence.json"
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

# 2) Walletbeat #865
print()
print("=" * 60)
print("Walletbeat #865")
print("=" * 60)
s, d = gh("GET", "/repos/walletbeat/walletbeat/issues/865")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"body: {d.get('body','')[:1500]}")
    s2, d2 = gh("GET", "/repos/walletbeat/walletbeat/issues/865/comments?per_page=10")
    if s2 == 200:
        for c in d2:
            print(f"  cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:300]}")
            print("  ---")

# 3) Check if there are still more open issues in the board
print()
print("=" * 60)
print("frantic-board open issues (other than #1)")
print("=" * 60)
s, d = gh("GET", "/repos/auscaster/frantic-board/issues?state=open&per_page=10")
if s == 200:
    for it in d:
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        print(f"    body: {it.get('body','')[:200]}")
