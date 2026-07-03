#!/usr/bin/env python3
"""Look for direct payment opportunities on owockibot.xyz (the actual platform)."""
import os, json, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
}

def call(url, method="GET", data=None, timeout=15):
    h = dict(HEADERS)
    if data is not None:
        if isinstance(data, dict): data = json.dumps(data)
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, method=method, headers=h)
    else:
        req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

# ============================================================
# 1) Check owockibot.xyz directly
# ============================================================
print("=" * 70)
print("1) OWOCKIBOT.XYZ DIRECT")
print("=" * 70)

# Top earners (proof they pay)
s, b = call("https://owockibot.xyz/api/bounty-board/stats")
print(f"  /api/bounty-board/stats: {s} {b[:500]}")

# Try to find claimer address format
s, b = call("https://owockibot.xyz/api/bounty/1")
print(f"  /api/bounty/1: {s} {b[:500]}")

s, b = call("https://owockibot.xyz/api/bounty-board?claimed_by=0xe87b4889baeee4ed60a1b2bfc7b3a6a17bce4ad6")
print(f"  bounties claimed by top earner: {s}")
if s == 200:
    j = json.loads(b)
    bs = j if isinstance(j, list) else j.get("bounties", [])
    print(f"  count: {len(bs)}")

# ============================================================
# 2) Find the OWOCKIBOT actual site contact
# ============================================================
print()
print("=" * 70)
print("2) OWOCKIBOT.XYZ contact info")
print("=" * 70)

text = urllib.request.urlopen("https://r.jina.ai/https://owockibot.xyz", context=ctx, timeout=30).read().decode()
# Look for @username, telegram, twitter, etc
import re
for pat in [r'twitter\.com/\w+', r'@(\w+)', r't\.me/\w+', r'discord\.gg/\w+', r'github\.com/\w+', r'warpcast\.com/\w+']:
    matches = re.findall(pat, text, re.IGNORECASE)
    if matches:
        print(f"  {pat}: {matches[:5]}")

# Look for @owockibot specifically
if "@owockibot" in text.lower():
    print(f"  ✓ Found @owockibot in owockibot.xyz text")

# ============================================================
# 3) Find real $$ bounty boards that pay
# ============================================================
print()
print("=" * 70)
print("3) SEARCH FOR REAL-$$ BOUNTY BOARDS")
print("=" * 70)

# GitHub topics for agent bounties
import subprocess
r = subprocess.run(["gh","search","repos","topic:agent-bounty","--sort","updated","--limit","20"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    print(f"  agent-bounty topic: {len(r.stdout.strip().split(chr(10)))} results")
    for line in r.stdout.strip().split("\n")[:10]:
        print(f"    {line[:120]}")

print()
r = subprocess.run(["gh","search","repos","topic:x402","--sort","stars","--limit","20"],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    print(f"  x402 topic: {len(r.stdout.strip().split(chr(10)))} results")
    for line in r.stdout.strip().split("\n")[:10]:
        print(f"    {line[:120]}")

# ============================================================
# 4) Check what other agents are doing (for ideas)
# ============================================================
print()
print("=" * 70)
print("4) AGENT ACTIVITY (X/Reddit/Twitter)")
print("=" * 70)

# Check @owockibot on X
r = subprocess.run(["gh","search","commits","--author","qingfeng312","--limit","5"],
                   capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    print(f"  qingfeng312 recent commits:")
    for line in r.stdout.strip().split("\n")[:5]:
        print(f"    {line[:120]}")

# ============================================================
# 5) Check $ / USDT on Base that I can swap to USDC
# ============================================================
print()
print("=" * 70)
print("5) ALL MY WALLETS - any tokens at all?")
print("=" * 70)

wallets = {
    "OPERATOR (no key)": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "D32A": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
    "0x86f36": "0x86f3666720d54c531c723201BA49403D7c42c564",
    "0xb108": "0xb10871882b12051b5531dBcaf0a564082aB41CeF",
}

for label, addr in wallets.items():
    s, b = call(f"https://base.blockscout.com/api/v2/addresses/{addr}/token-balances")
    if s == 200:
        items = b if isinstance(b, list) else b.get("items", [])
        non_zero = []
        for item in items:
            tok = item.get("token", {}) or {}
            sym = tok.get("symbol", "?")
            val = item.get("value", "0") or "0"
            if val.startswith("0x"):
                v = int(val, 16)
            else:
                v = int(val) if val else 0
            decimals = tok.get("decimals", 18) or 18
            human = v / (10 ** decimals)
            if human > 0:
                non_zero.append(f"{sym}={human}")
        if non_zero:
            print(f"  {label}: {', '.join(non_zero)}")
        else:
            print(f"  {label}: empty")
