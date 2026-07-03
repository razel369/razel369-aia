#!/usr/bin/env python3
"""Check runx + look at Frantic bounties + start fast auto-claimer."""
import json, urllib.request, urllib.error, subprocess, time, os, shutil

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
    """Run command with shell=True to handle missing executables."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

# 1) Check runx
print("=" * 60)
print("RUNX CLI")
print("=" * 60)
rc, out, err = run("runx --version", timeout=10)
print(f"  runx --version: rc={rc}, out={out[:200].strip()}, err={err[:200].strip()}")
rc, out, err = run("where runx", timeout=5)
print(f"  where runx: rc={rc}, out={out[:200].strip()}")
# Check npx
rc, out, err = run("npx runx --version", timeout=30)
print(f"  npx runx --version: rc={rc}, out={out[:200].strip()}, err={err[:300].strip()}")
# Check pip
rc, out, err = run("pip show runx", timeout=10)
print(f"  pip show runx: rc={rc}, out={out[:200].strip()}")
# Find runx on disk
for root in [r"C:\Users\rmalk\AppData\Roaming\npm", r"C:\Users\rmalk\AppData\Local\npm", r"C:\Program Files\nodejs"]:
    if os.path.exists(root):
        for f in os.listdir(root):
            if "runx" in f.lower():
                full = os.path.join(root, f)
                print(f"  found: {full} ({os.path.getsize(full) if os.path.isfile(full) else 'dir'})")

# 2) Stop old monitor
print()
print("=" * 60)
print("STOP OLD MONITOR")
print("=" * 60)
import psutil
killed = 0
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
            cmd = ' '.join(proc.info['cmdline'])
            if 'frantic_monitor' in cmd:
                print(f"  killing PID {proc.info['pid']}")
                proc.kill()
                killed += 1
    except: pass
print(f"  killed: {killed}")

# 3) Look at likely-deliverable Frantic bounties
print()
print("=" * 60)
print("FRANTIC LIKELY-DELIVERABLE BOUNTIES (status check)")
print("=" * 60)
candidates = [20, 19, 14, 7, 10, 5, 4, 3, 8, 9, 2, 6, 1, 50, 48, 47, 43, 31, 41, 45, 42, 39, 38, 35, 33]
for bid in candidates:
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
            cp = b.get("claimProgress",{})
            avail = cp.get("available", 0)
            print(f"  #{bid} ${price} ps={ps} ws={ws} avail={avail} {title}")
    time.sleep(0.1)
