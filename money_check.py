#!/usr/bin/env python3
"""Comprehensive money check: pushes, PRs, wallets, AIA worker, claimer."""
import subprocess, json, time, os, urllib.request, ssl

def sh(cmd, timeout=30):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str))
    return r.returncode, r.stdout, r.stderr

# ============================================================
# 1) RAZEL369-AIA REPO STATUS + PUSH
# ============================================================
print("=" * 70)
print("1) RAZEL369-AIA REPO")
print("=" * 70)
os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
print(f"  cwd: {os.getcwd()}")

rc, out, err = sh("git remote -v")
print(f"  remotes: {out.strip()}")

rc, out, err = sh("git status --short")
print(f"  status: {out[:500]}")

rc, out, err = sh("git log --oneline -5")
print(f"  last 5 commits: {out}")

rc, out, err = sh('git log --oneline origin/main..HEAD 2>&1')
unpushed_count = len([l for l in out.strip().split('\n') if l]) if out.strip() else 0
print(f"  unpushed count: {unpushed_count}")
if unpushed_count > 0:
    print(f"  unpushed: {out[:500]}")

# Push if there are commits
if unpushed_count > 0:
    rc, out, err = sh("git push origin main", timeout=120)
    print(f"  push: rc={rc}")
    if err: print(f"    err: {err[:500]}")

# Check GitHub
rc, out, err = sh('gh repo view razel369/razel369-aia --json name,description,url,isPrivate,defaultBranchRef 2>&1')
print(f"  gh repo: {out[:300]}")

# ============================================================
# 2) ALL PRs — review status, comments, merge status
# ============================================================
print()
print("=" * 70)
print("2) ALL MY PRs")
print("=" * 70)
os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

# We know our PRs:
# - cyrilawoyemi99-max/owockibot-bounty-sync-#37 (owk-004 $400 badges)
# - cyrilawoyemi99-max/owockibot-bounty-sync-#39 (owk-005 $1,200 audit)
# - cyrilawoyemi99-max/owockibot-bounty-sync-#40 (owk-001 $750 dashboard)
# - dwebagents/AgentPipe#1941 (fake ETH)
# - jessedaustin93/Open-Aeon#2 (test)
PR_LIST = [
    ("cyrilawoyemi99-max", "owockibot-bounty-sync-", 37, "owk-004 $400 badges"),
    ("cyrilawoyemi99-max", "owockibot-bounty-sync-", 39, "owk-005 $1,200 audit"),
    ("cyrilawoyemi99-max", "owockibot-bounty-sync-", 40, "owk-001 $750 dashboard"),
    ("dwebagents", "AgentPipe", 1941, "AgentPipe fake ETH"),
    ("jessedaustin93", "Open-Aeon", 2, "Open-Aeon test")
]
for owner, repo, num, desc in PR_LIST:
    rc, out, err = sh(f'gh api repos/{owner}/{repo}/pulls/{num} 2>&1')
    if rc == 0:
        pr = json.loads(out)
        print(f"  PR #{num} ({desc})")
        print(f"    state={pr.get('state')} mergeable={pr.get('mergeable')} merged={pr.get('merged')}")
        print(f"    title: {pr.get('title')[:80]}")
        print(f"    additions={pr.get('additions')} deletions={pr.get('deletions')}")
        print(f"    comments={pr.get('comments')} review_comments={pr.get('review_comments')}")
        print(f"    url: {pr.get('html_url')}")
        # Get review status
        rc2, out2, err2 = sh(f'gh api repos/{owner}/{repo}/pulls/{num}/reviews 2>&1')
        if rc2 == 0:
            reviews = json.loads(out2)
            if reviews:
                print(f"    reviews:")
                for r in reviews:
                    print(f"      - {r.get('state')} by {r.get('user', {}).get('login')}: {r.get('body','')[:100]}")
            else:
                print(f"    reviews: none")
        # Get issue comments
        rc3, out3, err3 = sh(f'gh api repos/{owner}/{repo}/issues/{num}/comments 2>&1')
        if rc3 == 0:
            comments = json.loads(out3)
            external_comments = [c for c in comments if c.get('user', {}).get('login') != 'razel369']
            if external_comments:
                print(f"    external comments ({len(external_comments)}):")
                for c in external_comments:
                    print(f"      - {c.get('user', {}).get('login')}: {c.get('body','')[:150]}")
            else:
                print(f"    comments: only my own")
    else:
        print(f"  PR #{num} ({desc}): ERR {err[:200]}")
    print()

# ============================================================
# 3) AIA X402 WORKER STATS
# ============================================================
print("=" * 70)
print("3) AIA X402 WORKER")
print("=" * 70)

ctx = ssl.create_default_context()
try:
    req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/health", method="GET")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        body = r.read().decode('utf-8', errors='replace')
        print(f"  /health: {r.status} ({len(body)}b)")
        print(f"    {body[:400]}")
except Exception as e:
    print(f"  /health ERR: {e}")

try:
    req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/.well-known/mcp.json", method="GET")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        body = r.read().decode('utf-8', errors='replace')
        print(f"  mcp.json: {r.status} ({len(body)}b)")
        print(f"    {body[:600]}")
except Exception as e:
    print(f"  mcp.json ERR: {e}")

try:
    req = urllib.request.Request("https://aia-x402.rmalka06.workers.dev/v1/signals", method="GET")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        body = r.read().decode('utf-8', errors='replace')
        print(f"  /v1/signals: {r.status} ({len(body)}b)")
        print(f"    {body[:400]}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f"  /v1/signals: {e.code} ({len(body)}b)")
    print(f"    {body[:600]}")
except Exception as e:
    print(f"  /v1/signals ERR: {e}")

# ============================================================
# 4) FRANTIC WALLET (agent-b62bf6)
# ============================================================
print()
print("=" * 70)
print("4) FRANTIC AGENT STATUS")
print("=" * 70)

# Frantic uses kid-based auth
KID = "agent-b62bf6"
TOKEN_FILE = r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE) as f:
        st = json.load(f)
    token = st.get("token", "")
    print(f"  kid: {KID}")
    print(f"  token prefix: {token[:30]}...")

    # MCP call
    try:
        url = "https://www.frantic.studio/api/mcp"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("Authorization", f"Bearer {token}")
        body = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "agent_status", "arguments": {"kid": KID}}
        }).encode()
        with urllib.request.urlopen(req, data=body, context=ctx, timeout=20) as r:
            data = r.read().decode('utf-8', errors='replace')
            print(f"  agent_status: {r.status}")
            print(f"    {data[:600]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"  agent_status: {e.code}")
        print(f"    {body[:400]}")
    except Exception as e:
        print(f"  agent_status ERR: {e}")

    # Bounty list
    try:
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("Authorization", f"Bearer {token}")
        body = json.dumps({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "list_bounties", "arguments": {"include_closed": True, "limit": 50}}
        }).encode()
        with urllib.request.urlopen(req, data=body, context=ctx, timeout=20) as r:
            data = r.read().decode('utf-8', errors='replace')
            print(f"  list_bounties: {r.status}")
            try:
                j = json.loads(data)
                items = j.get("result", {}).get("content", [])
                for it in items[:5]:
                    print(f"    {it[:200]}")
            except:
                print(f"    {data[:600]}")
    except Exception as e:
        print(f"  list_bounties ERR: {e}")

# ============================================================
# 5) CINDERWRIGHT STATUS
# ============================================================
print()
print("=" * 70)
print("5) CINDERWRIGHT")
print("=" * 70)

CW_KEY = "sk_cw_058d7def416df8b71958024a4c88afac"
SUB_ID = "sub_1783076946558"

# Check AIA in discover
try:
    url = f"https://api.ideafactorylab.org/discover?q=aia&limit=20"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        data = json.loads(r.read().decode())
        services = data.get("services", data) if isinstance(data, dict) else data
        if isinstance(services, list):
            print(f"  /discover q=aia: {len(services)} hits")
            for s in services[:5]:
                name = s.get("name", s.get("title", "?"))
                url_s = s.get("url", s.get("endpoint", "?"))
                print(f"    - {name} -> {url_s}")
        else:
            print(f"  /discover: {data}")
except Exception as e:
    print(f"  /discover ERR: {e}")

# Submission status
try:
    url = f"https://api.ideafactorylab.org/submissions/{SUB_ID}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {CW_KEY}")
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        data = json.loads(r.read().decode())
        print(f"  submission {SUB_ID}: {r.status}")
        print(f"    {data}")
except urllib.error.HTTPError as e:
    print(f"  submission: {e.code} {e.read().decode()[:300]}")
except Exception as e:
    print(f"  submission ERR: {e}")

# Proxy account balance
try:
    url = f"https://api.ideafactorylab.org/proxy/balance"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {CW_KEY}")
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        data = json.loads(r.read().decode())
        print(f"  proxy balance: {r.status}")
        print(f"    {data}")
except urllib.error.HTTPError as e:
    print(f"  proxy balance: {e.code} {e.read().decode()[:300]}")
except Exception as e:
    print(f"  proxy balance ERR: {e}")

# ============================================================
# 6) OPERATOR USDC WALLET ON BASE
# ============================================================
print()
print("=" * 70)
print("6) OPERATOR USDC WALLET ON BASE")
print("=" * 70)

WALLET = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

# Basescan API (free tier, no key needed for basic calls)
# Use eth_call via public RPC for USDC balance
try:
    # USDC on Base: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
    USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    # balanceOf(address) selector: 0x70a08231
    addr_clean = WALLET[2:].lower().zfill(64)
    data = "0x70a08231" + addr_clean
    rpc_payload = {
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": USDC_BASE, "data": data}, "latest"]
    }
    req = urllib.request.Request("https://mainnet.base.org",
                                 data=json.dumps(rpc_payload).encode(),
                                 method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        result = json.loads(r.read().decode())
        bal_hex = result.get("result", "0x0")
        bal_int = int(bal_hex, 16)
        # USDC has 6 decimals
        bal_usdc = bal_int / 1_000_000
        print(f"  USDC balance: ${bal_usdc:.6f} ({bal_int} raw)")
except Exception as e:
    print(f"  USDC balance ERR: {e}")

# Native ETH
try:
    rpc_payload = {
        "jsonrpc": "2.0", "id": 1, "method": "eth_getBalance",
        "params": [WALLET, "latest"]
    }
    req = urllib.request.Request("https://mainnet.base.org",
                                 data=json.dumps(rpc_payload).encode(),
                                 method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        result = json.loads(r.read().decode())
        bal_hex = result.get("result", "0x0")
        bal_int = int(bal_hex, 16)
        bal_eth = bal_int / 1e18
        print(f"  ETH balance: {bal_eth:.8f} ETH")
except Exception as e:
    print(f"  ETH balance ERR: {e}")

# ============================================================
# 7) FRANTIC CLAIMER LOG
# ============================================================
print()
print("=" * 70)
print("7) FRANTIC CLAIMER LOG")
print("=" * 70)

log_path = r"C:\Users\rmalk\projects\razel369-aia\frantic_claimer.log"
if os.path.exists(log_path):
    with open(log_path) as f:
        lines = f.readlines()
    print(f"  log: {log_path} ({len(lines)} lines)")
    print("  last 20:")
    for line in lines[-20:]:
        print(f"    {line.rstrip()}")
else:
    print(f"  no log: {log_path}")

# Check process
rc, out, err = sh("tasklist | findstr /i python", timeout=10)
print(f"  python procs: {out[:500]}")

# ============================================================
# 8) SHOW HN
# ============================================================
print()
print("=" * 70)
print("8) SHOW HN")
print("=" * 70)
show_path = r"C:\Users\rmalk\projects\razel369-aia\show_hn_v2.md"
if os.path.exists(show_path):
    with open(show_path) as f:
        content = f.read()
    print(f"  file: {show_path} ({len(content)}b)")
    print(f"  first 200: {content[:200]}")
