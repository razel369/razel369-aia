#!/usr/bin/env python3
"""Frantic monitor - polls every 60s for new paid bounties."""
import json, urllib.request, urllib.error, time, os

LOG = r"C:\Users\rmalk\projects\razel369-aia\frantic_monitor.log"
STATE = r"C:\Users\rmalk\projects\razel369-aia\frantic_monitor_state.json"

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

state = {}
if os.path.exists(STATE):
    with open(STATE) as f:
        try: state = json.loads(f.read())
        except: pass
last_known_open = state.get("open_bounties", [])
last_known_moved = state.get("moved", 0)
log("start: last_open=" + str([b.get("number") for b in last_known_open]) + " last_moved=$" + str(last_known_moved))

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
            cur_moved = b.get("moved_usd",0) or 0
            cur_numbers = [x.get("number") for x in cur_open]
            old_numbers = [x.get("number") for x in last_known_open]
            new_paid = [x for x in cur_open if x.get("number") not in old_numbers and x.get("price_usd",0) > 0]
            if new_paid:
                log("!!! NEW PAID: " + json.dumps([(n.get("number"), n.get("price_usd"), n.get("title","")[:50]) for n in new_paid]))
            if cur_numbers != old_numbers:
                log("open change: " + str(old_numbers) + " -> " + str(cur_numbers))
            if cur_moved != last_known_moved:
                log("moved change: $" + str(last_known_moved) + " -> $" + str(cur_moved))
            with open(STATE, "w") as f:
                json.dump({"open_bounties": cur_open, "moved": cur_moved, "ts": time.time()}, f)
            last_known_open = cur_open
            last_known_moved = cur_moved
    except Exception as e:
        log("err: " + str(e))
    time.sleep(60)
