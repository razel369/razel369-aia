#!/usr/bin/env python3
"""FAST Frantic auto-claimer - polls every 5s, auto-claims paid bounties."""
import json, urllib.request, urllib.error, time, os

LOG = r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.log"
STATE = r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer_state.json"

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
        f.write(line + "\n")

# Load token
TOK_FILE = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json"
with open(TOK_FILE) as f:
    raw = f.read()
    if raw[:3] == "\xef\xbb\xbf":
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
