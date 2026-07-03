#!/usr/bin/env python3
"""Get full Frantic delivery rejection reason."""
import json, urllib.request, urllib.error

def fetch(url, method="GET", data=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if data is not None:
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    else:
        body = None
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

# Read ledger (full feed)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_ledger","arguments":{}}
})
sc = d.get("result",{}).get("structuredContent",{}) if isinstance(d, dict) else {}
print("Ledger full:")
print(json.dumps(sc, indent=2)[:5000])
