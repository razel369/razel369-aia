#!/usr/bin/env python3
"""Register on Cinderwright referral program + get bounty JSON + explore the ecosystem."""
import json, urllib.request, urllib.error

def fetch(url, headers=None):
    h = {"User-Agent":"Mozilla/5.0","Accept":"*/*"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e: return -1, str(e)

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

# 1) Get the .well-known/bounties.json
print("=" * 60)
print("CINDERWRIGHT: .well-known/bounties.json")
print("=" * 60)
s, d = fetch("https://api.ideafactorylab.org/.well-known/bounties.json")
if s == 200 and isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])
elif isinstance(d, str):
    print(f"  status: {s}, raw: {d[:1000]}")
else:
    print(f"  status: {s}")

# 2) Get the earn docs
print()
print("=" * 60)
print("CINDERWRIGHT: /earn")
print("=" * 60)
s, d = fetch("https://api.ideafactorylab.org/earn")
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:2000])

# 3) Register
print()
print("=" * 60)
print("REGISTER on Cinderwright")
print("=" * 60)
s, d = fetch(f"https://api.ideafactorylab.org/referral/join?wallet={WALLET}")
print(f"  status: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2))
elif isinstance(d, str):
    print(f"  raw: {d[:1000]}")

# 4) Look at /discover to see what services are on Cinderwright
print()
print("=" * 60)
print("CINDERWRIGHT: /discover")
print("=" * 60)
for q in ["ai", "agent", "data", "signal"]:
    s, d = fetch(f"https://api.ideafactorylab.org/discover?q={q}")
    if s == 200 and isinstance(d, dict):
        svcs = d.get("services",[]) or d.get("items",[]) or d.get("data",[])
        if svcs:
            print(f"  q={q}: {len(svcs)} services")
            for sv in svcs[:3]:
                print(f"    {sv.get('name','')[:50]} ${sv.get('price','')}")
            break

# 5) Save wallet info
print()
print("=" * 60)
print("SAVE registration state")
print("=" * 60)
import os
state_path = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\cinderwright.json"
os.makedirs(os.path.dirname(state_path), exist_ok=True)
state = {"wallet": WALLET, "registration_response": d if isinstance(d, dict) else str(d)[:500]}
if s == 200 and isinstance(d, dict):
    state["ref_code"] = d.get("code") or d.get("referral_code") or d.get("ref")
    state["ref_url"] = d.get("ref_url") or d.get("url")
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
print(f"  saved: {state_path}")
print(f"  state: {json.dumps(state)[:500]}")
