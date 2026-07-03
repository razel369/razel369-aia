#!/usr/bin/env python3
"""Set up FAST Frantic monitor with auto-claim + check runx + prep work."""
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

# 1) Check if runx is installed
print("=" * 60)
print("RUNX CLI check")
print("=" * 60)
r = subprocess.run(["runx","--version"], capture_output=True, text=True, timeout=10)
print(f"  runx --version: rc={r.returncode}, out={r.stdout[:200]}, err={r.stderr[:200]}")
# Try with npx
r = subprocess.run(["npx","runx","--version"], capture_output=True, text=True, timeout=30)
print(f"  npx runx --version: rc={r.returncode}, out={r.stdout[:200]}, err={r.stderr[:200]}")
# Try via Python pip
r = subprocess.run(["pip","show","runx"], capture_output=True, text=True, timeout=10)
print(f"  pip show runx: rc={r.returncode}, out={r.stdout[:200]}")
# Look for runx via python
r = subprocess.run(["python","-c","import runx; print(runx.__version__)"], capture_output=True, text=True, timeout=10)
print(f"  python import runx: rc={r.returncode}, out={r.stdout[:200]}, err={r.stderr[:200]}")
# Look for runx executable
import shutil
for path in [shutil.which("runx"), shutil.which("runx.exe")]:
    print(f"  which runx: {path}")
# Look on disk
for root in [r"C:\Users\rmalk\AppData\Roaming\npm", r"C:\Program Files\nodejs"]:
    if os.path.exists(root):
        for f in os.listdir(root):
            if "runx" in f.lower():
                print(f"  found: {os.path.join(root, f)}")

# 2) Check Frantic MCP for the runx skill info
print()
print("=" * 60)
print("FRANTIC: details on likely-deliverable bounties")
print("=" * 60)
# Look at the verifier/web-research bounties specifically
for bid in [20, 19, 14, 7, 10, 5, 4, 3, 8, 9, 2, 6, 1, 50, 48, 47, 43, 31, 41, 45, 42, 39]:
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
            title = b.get("title","")[:60]
            if ps in ["visible", "open"] or ws in ["open", "available"]:
                print(f"  *** #{bid} ${price} ps={ps} ws={ws} {title}")
                print(f"       desc: {b.get('description','')[:300]}")
    time.sleep(0.1)

# 3) Save runx availability status
print()
print("=" * 60)
print("NEXT: Stop old monitor, start fast auto-claimer")
print("=" * 60)

# Stop the old monitor
import psutil
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    if proc.info['name'] == 'python.exe' and proc.info['cmdline'] and 'frantic_monitor' in ' '.join(proc.info['cmdline']):
        print(f"  killing PID {proc.info['pid']}: {' '.join(proc.info['cmdline'][:3])}")
        try: proc.kill()
        except: pass
