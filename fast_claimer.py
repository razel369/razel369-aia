#!/usr/bin/env python3
"""Set up FAST Frantic auto-claimer + look at Spectral-Finance/lux $1,500 bounty."""
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

# 1) Look at Spectral-Finance/lux #75 ($1,500 USDC)
print("=" * 60)
print("SPECTRAL-FINANCE/LUX #75 ($1,500 USDC)")
print("=" * 60)
r = subprocess.run(["gh","api","repos/Spectral-Finance/lux/issues/75"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: issue = json.loads(r.stdout)
    except: issue = {}
    print(f"  title: {issue.get('title')}")
    print(f"  state: {issue.get('state')}")
    labels = [l.get("name","") for l in issue.get("labels",[])]
    print(f"  labels: {labels}")
    print(f"  body: {issue.get('body','')[:2000]}")
    print()
    print("  Comments:")
    rc2 = subprocess.run(["gh","api","repos/Spectral-Finance/lux/issues/75/comments"],
                         capture_output=True, text=True, timeout=30)
    if rc2.returncode == 0:
        try: comments = json.loads(rc2.stdout)
        except: comments = []
        for c in comments[:8]:
            print(f"    @{c.get('user',{}).get('login','?')}: {c.get('body','')[:300]}")

# 2) Look at Spectral-Finance/lux repo description
print()
print("=" * 60)
print("SPECTRAL-FINANCE/LUX repo")
print("=" * 60)
r = subprocess.run(["gh","api","repos/Spectral-Finance/lux"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: repo = json.loads(r.stdout)
    except: repo = {}
    print(f"  desc: {repo.get('description','')}")
    print(f"  stars: {repo.get('stargazers_count')}, forks: {repo.get('forks_count')}")
    print(f"  topics: {repo.get('topics',[])}")
    print(f"  default_branch: {repo.get('default_branch')}")
    print(f"  html: {repo.get('html_url')}")

# 3) Look at Sifchain/sifnode $1000 bounties
print()
print("=" * 60)
print("SIFCHAIN/SIFNODE #524 ($1000 USDC)")
print("=" * 60)
r = subprocess.run(["gh","api","repos/Sifchain/sifnode/issues/524"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    try: issue = json.loads(r.stdout)
    except: issue = {}
    print(f"  title: {issue.get('title')}")
    print(f"  state: {issue.get('state')}")
    print(f"  body: {issue.get('body','')[:1500]}")

# 4) Write the FAST Frantic auto-claimer
print()
print("=" * 60)
print("WRITE FAST FRANTIC AUTO-CLAIMER")
print("=" * 60)
claimer = '''#!/usr/bin/env python3
"""FAST Frantic auto-claimer - polls every 5s, auto-claims paid bounties."""
import json, urllib.request, urllib.error, time, os

LOG = r"C:\\Users\\rmalk\\projects\\razel369-aia\\frantic_claimer.log"
STATE = r"C:\\Users\\rmalk\\projects\\razel369-aia\\frantic_claimer_state.json"

def fetch(url, headers=None, method="GET", data=None, timeout=15):
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
    except Exception as e:
        return -1, str(e)

def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = ts + " " + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\\n")

# Load token
TOK_FILE = r"C:\\Users\\rmalk\\projects\\razel369-aia\\.agent-credentials\\frantic_state.json"
with open(TOK_FILE) as f:
    raw = f.read()
    if raw[:3] == "\\xef\\xbb\\xbf":
        raw = raw[3:]
    st = json.loads(raw)
KID = st.get("agent_kid")
TOKEN = st.get("agent_token")

log("start: kid=" + KID)

# Load state
state = {}
if os.path.exists(STATE):
    with open(STATE) as f:
        try: state = json.loads(f.read())
        except: pass
last_known_open = set(state.get("open_numbers", []))
last_known_paid = set(state.get("paid_numbers", []))

while True:
    try:
        s, d = fetch("https://api.gofrantic.com/mcp", method="POST",
            headers={"Accept":"application/json, text/event-stream"},
            data={"jsonrpc":"2.0","id":1,"method":"tools/call",
                  "params":{"name":"frantic.read_board","arguments":{}}})
        if isinstance(d, dict):
            sc = d.get("result",{}).get("structuredContent",{})
            b = sc.get("board",{})
            cur_open = b.get("open_bounties",[]) or []
            cur_paid = [x.get("number") for x in cur_open if x.get("price_usd", 0) > 0]
            cur_set = set(cur_paid)
            new_paid = cur_set - last_known_paid
            if new_paid:
                # Auto-claim each new paid bounty
                for bid in new_paid:
                    log("!!! NEW PAID BOUNTY: #" + str(bid) + " — AUTO-CLAIMING")
                    s2, d2 = fetch("https://api.gofrantic.com/mcp", method="POST",
                        headers={"Accept":"application/json, text/event-stream"},
                        data={"jsonrpc":"2.0","id":1,"method":"tools/call",
                              "params":{"name":"frantic.claim_bounty",
                                        "arguments":{"bounty":str(bid),"agent_kid":KID,"agent_token":TOKEN}}})
                    if isinstance(d2, dict):
                        sc2 = d2.get("result",{}).get("structuredContent",{})
                        if sc2.get("ok"):
                            log("  +++ CLAIMED #" + str(bid) + " claim_id=" + str(sc2.get("claim_id","")))
                        else:
                            log("  --- CLAIM FAILED: " + str(sc2.get("error","")) + " " + str(sc2.get("message","")))
            # Save state
            with open(STATE, "w") as f:
                json.dump({"open_numbers": list(cur_set), "paid_numbers": list(cur_set), "ts": time.time()}, f)
            last_known_paid = cur_set
    except Exception as e:
        log("err: " + str(e))
    time.sleep(5)
'''
with open(r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.py", "w", encoding="utf-8") as f:
    f.write(claimer)
claimer_path = r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.py"
print(f"  claimer saved: {os.path.getsize(claimer_path)}b")

# 5) Start the auto-claimer
print()
print("Starting fast auto-claimer...")
import subprocess
r = subprocess.Popen(["python","-X","utf8",r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.py"],
                     stdout=open(r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.out","w"),
                     stderr=open(r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.err","w"),
                     creationflags=0x00000008)  # DETACHED_PROCESS
print(f"  started PID {r.pid}")
time.sleep(3)
if os.path.exists(r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.log"):
    with open(r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.log") as f:
        print("  log:")
        print(f.read()[:500])
