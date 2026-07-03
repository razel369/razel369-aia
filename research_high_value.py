#!/usr/bin/env python3
"""Research high-value opportunities: lux, mergeos, HELPDESK, ai-research."""
import json, urllib.request, urllib.error, urllib.parse

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

def fetch(url, headers=None, method="GET", data=None, timeout=20):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json"}
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
        return e.code, e.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return -1, str(e)

# 1) lux bounties
print("=" * 60)
print("lux repo bounties")
print("=" * 60)
s, d = gh("/orgs/lux/repos?per_page=20")
if s == 200:
    for r in d:
        print(f"  {r.get('full_name')}: {r.get('description','')[:80]}")
print()
s, d = gh("/repos/lux/lux/issues?state=open&per_page=30")
if s == 200:
    for it in d:
        if "pull_request" in it: continue
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        body = it.get("body","") or ""
        if "$" in body or "USDC" in body or "bounty" in (it.get("title","") or "").lower():
            print(f"    body: {body[:600]}")

# 2) mergeos
print()
print("=" * 60)
print("mergeos")
print("=" * 60)
s, d = gh("/repos/mergeos/repo/issues/64")
if s == 200:
    print(f"title: {d.get('title')}")
    print(f"body: {d.get('body','')[:1500]}")
s, d = gh("/repos/mergeos/repo/issues?state=open&per_page=20")
if s == 200:
    for it in d:
        if "pull_request" in it: continue
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")

# 3) HELPDESK.AI
print()
print("=" * 60)
print("HELPDESK.AI")
print("=" * 60)
for n in [3210, 3211, 3212, 3213]:
    s, d = gh(f"/repos/HELPDESK-AI/HELPDESK.AI/issues/{n}")
    if s == 200:
        print(f"  #{n} {d.get('title')}")
        print(f"    body: {d.get('body','')[:500]}")
        print(f"    state: {d.get('state')}, comments: {d.get('comments')}")
        s2, d2 = gh(f"/repos/HELPDESK-AI/HELPDESK.AI/issues/{n}/comments?per_page=5")
        if s2 == 200:
            for c in d2[:3]:
                print(f"      cmt by {c.get('user',{}).get('login')}: {c.get('body','')[:200]}")

# 4) owocki-bot/ai-bounty-board
print()
print("=" * 60)
print("owocki-bot/ai-bounty-board")
print("=" * 60)
s, d = gh("/repos/owocki-bot/ai-bounty-board/readme")
if s == 200:
    import base64
    print(base64.b64decode(d.get("content","")).decode("utf-8")[:2000])
s, d = gh("/repos/owocki-bot/ai-bounty-board/issues?state=open&per_page=20")
if s == 200:
    for it in d:
        if "pull_request" in it: continue
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        print(f"    body: {(it.get('body','') or '')[:400]}")

# 5) Find the Frantic board link
print()
print("=" * 60)
print("Frantic board updated")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_board","arguments":{}}
})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}")
    for ob in b.get("open_bounties", []):
        print(f"  #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title')[:60]}")
    # Last 10 events
    print()
    print("Recent events:")
    for e in b.get("feed",[])[:10]:
        print(f"  {e.get('at','')[:19]} {e.get('kind'):>10}  {e.get('text','')[:120]}")
