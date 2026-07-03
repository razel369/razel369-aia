#!/usr/bin/env python3
"""Check runx Python pkg + get full AgentPipe paystub + check for high-number Frantic bounties."""
import json, urllib.request, urllib.error, subprocess, time, os

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

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

# 1) Check what runx Python pkg is
print("=" * 60)
print("RUNX PYTHON")
print("=" * 60)
rc, out, err = run("python -X utf8 -c \"import runx; print(dir(runx)); print('version:', getattr(runx, '__version__', 'n/a'))\"", timeout=10)
print(f"  rc={rc}, out={out[:500]}")
print(f"  err={err[:200]}")
rc, out, err = run("pip show runx", timeout=10)
print(f"  pip show runx: {out[:500]}")

# 2) Get full AgentPipe paystub
print()
print("=" * 60)
print("AGENTPIPE PR #1941 — full paystub")
print("=" * 60)
r = subprocess.run(["gh","api","repos/dwebagents/AgentPipe/issues/1941/comments?per_page=20"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: comments = json.loads(r.stdout)
    except: pass
    for c in comments:
        u = c.get("user",{}).get("login","?")
        body = c.get("body","")
        if "PAYSTUB" in body or "merge" in body.lower() or "approved" in body.lower() or "reward" in body.lower():
            print(f"  @{u}:")
            print(f"    {body}")
            print()

# 3) Get latest AgentPipe issues to see if there are new bounty issues
print()
print("=" * 60)
print("AGENTPIPE issues — find new bounties")
print("=" * 60)
r = subprocess.run(["gh","api","repos/dwebagents/AgentPipe/issues?state=open&per_page=20"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: issues = json.loads(r.stdout)
    except: issues = []
    for i in issues[:10]:
        if "pull" not in i.get("html_url",""):
            labels = [l.get("name","") for l in i.get("labels",[])]
            print(f"  #{i.get('number')} {i.get('title','')[:70]}")
            print(f"    labels: {labels}")
            print(f"    body: {i.get('body','')[:200]}")

# 4) Check for any new paid Frantic bounties (poll NOW)
print()
print("=" * 60)
print("FRANTIC: poll now (any new paid)")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
    headers={"Accept":"application/json, text/event-stream"},
    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
          "params":{"name":"frantic.read_board","arguments":{}}})
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}")
    for ob in b.get("open_bounties",[]):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:60]}")
    for e in b.get("feed",[])[:5]:
        print(f"  {e.get('at','')[:19]} {e.get('kind','?'):>10}  {e.get('text','')[:100]}")

# 5) Check new Frantic bounties 50-100 (in case I missed some)
print()
print("=" * 60)
print("FRANTIC: scan 50-100 (any open paid)")
print("=" * 60)
for bid in range(50, 101):
    s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
        headers={"Accept":"application/json, text/event-stream"},
        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
              "params":{"name":"frantic.get_bounty","arguments":{"id":str(bid)}}})
    if isinstance(d, dict):
        sc = d.get("result",{}).get("structuredContent",{})
        b = sc.get("bounty",{}) if isinstance(sc.get("bounty"), dict) else sc
        if isinstance(b, dict):
            ps = b.get("postingStatus","?")
            ws = b.get("workStatus","?")
            price = b.get("priceUsd") or 0
            cp = b.get("claimProgress",{})
            avail = cp.get("available", 0)
            if (ps == "visible" and ws in ["open","available"]) or avail > 0:
                print(f"  *** #{bid} ${price} ps={ps} ws={ws} avail={avail} {b.get('title','')[:60]}")
    time.sleep(0.1)
