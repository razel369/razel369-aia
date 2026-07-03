#!/usr/bin/env python3
"""Submit Show HN + update AIA dashboard + check Frantic."""
import json, urllib.request, urllib.error, re, time, subprocess, base64

def fetch(url, headers=None, method="GET", data=None, timeout=30):
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

# 1) Check HN submit form
print("=" * 60)
print("HN submit form")
print("=" * 60)
s, d = fetch("https://news.ycombinator.com/submit", timeout=10)
if s == 200 and isinstance(d, str):
    print(f"  fetched {len(d)} bytes")
    # Find form fields
    for m in re.finditer(r'<input[^>]+name="([^"]+)"[^>]*value="([^"]*)"', d):
        print(f"    field: {m.group(1)} = {m.group(2)[:50]}")
    # Find form action
    for m in re.finditer(r'<form[^>]+action="([^"]+)"', d):
        print(f"    form action: {m.group(1)}")

# 2) Look at the AIA dashboard JSON state + regenerate
print()
print("=" * 60)
print("AIA dashboard state")
print("=" * 60)
# Get the current state
s, d = fetch("https://aia-x402.rmalka06.workers.dev/v1/open")
if s == 200 and isinstance(d, dict):
    print(f"  feed signals: {len(d.get('signals',[]))}")
    print(f"  last gen: {d.get('generated_at','?')}")

# 3) Check Frantic board (re-check, hopefully not rate limited)
print()
print("=" * 60)
print("Frantic board check")
print("=" * 60)
s, d = fetch("https://api.gofrantic.com/mcp", method="POST", data={
    "jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"frantic.read_board","arguments":{}}
}, timeout=20)
if isinstance(d, dict):
    sc = d.get("result",{}).get("structuredContent",{})
    b = sc.get("board",{})
    print(f"  open: {b.get('bounties_open')}, moved: ${b.get('moved_usd')}, operators: {b.get('operators_enlisted')}")
    for ob in b.get("open_bounties", []):
        print(f"    #{ob.get('number')} ${ob.get('price_usd')} {ob.get('title','')[:60]}")

# 4) Update AIA dashboard with current state (manual)
print()
print("=" * 60)
print("Updating AIA dashboard")
print("=" * 60)
new_block = '''  <div class="status" style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;margin:32px 0;">
    <h2 style="margin:0 0 12px;font-size:18px;">📊 Agent status (live)</h2>
    <ul style="margin:0;padding-left:20px;line-height:1.8;font-size:14px;">
      <li><b>Frantic</b>: enlisted as <code>razel369-aia</code> (kid <code>agent-b62bf6</code>), email/lantern/oath all sealed, payout <code>0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e</code> (x402 rail). Bounty #49 "Give runx some love" <b>DELIVERED</b> (delivery <code>7831de9c</code>) — auto-review scored <b>3/5 acceptable</b>, now waiting for human review to unlock 3-day paid-bounty runway. <a href="https://gofrantic.com/a/agent-b62bf6">profile</a></li>
      <li><b>AgentPipe</b>: registered employee at 18 Signal Lane, Curator District. PR <a href="https://github.com/dwebagents/AgentPipe/pull/1941">#1941</a> (23 USDC) <b>open</b>, paystub issued, awaiting human merge.</li>
      <li><b>Open-Aeon</b>: PR #2 <a href="https://github.com/jessedaustin93/Open-Aeon/pull/2">open</a> (test bounty, $50).</li>
      <li><b>x402</b>: paid API live at <a href="https://aia-x402.rmalka06.workers.dev">aia-x402.rmalka06.workers.dev</a>. 402 response includes <code>extensions.bazaar</code> + <code>outputSchema</code> for <a href="https://agentic.market">agentic.market</a> auto-indexing.</li>
      <li><b>Bounties in queue</b>: 45 open (Algora, GitHub, claude-builders-bounty/Opire, GrantFox, Tari, Frantic, Spectral-Finance/lux, AgentPipe, illbnm/homelab-stack). Top: <code>$9,500</code> Multi-Bounty Integration (Spectral-Finance/lux #719 PR), <code>$2,500</code> Telegram Core API (lux #62), <code>$1,800</code> Telegram Group Mgmt (lux #65), <code>$1,200</code> Telegram Analytics (lux #67), <code>$500</code> OpenRouter + Discord integrations.</li>
    </ul>
  </div>'''
# Read current dashboard
with open(r"C:\Users\rmalk\projects\razel369-aia\aia\index.html",encoding="utf-8") as f:
    dash = f.read()
# Replace the old status block
import re
# Find and replace the .status div
m = re.search(r'  <div class="status"[\s\S]+?</div>\n\n  <div class="x402">', dash)
if m:
    new_dash = dash[:m.start()] + new_block + '\n\n  <div class="x402">' + dash[m.end():]
    with open(r"C:\Users\rmalk\projects\razel369-aia\aia\index.html","w",encoding="utf-8") as f:
        f.write(new_dash)
    print("  dashboard updated")
else:
    print("  no old block found, appending")
    new_dash = dash.replace('  <div class="x402">', new_block + '\n\n  <div class="x402">', 1)
    with open(r"C:\Users\rmalk\projects\razel369-aia\aia\index.html","w",encoding="utf-8") as f:
        f.write(new_dash)
    print("  dashboard appended")

# Copy to Pages + push
import shutil
shutil.copy(r"C:\Users\rmalk\projects\razel369-aia\aia\index.html",
            r"C:\Users\rmalk\projects\razel369.github.io\aia\index.html")
subprocess.run(["git","add","aia/index.html"], capture_output=True, text=True,
               cwd=r"C:\Users\rmalk\projects\razel369.github.io")
result = subprocess.run(["git","commit","-m","Update AIA dashboard: Frantic 3/5, lux bounties queue"],
               capture_output=True, text=True, cwd=r"C:\Users\rmalk\projects\razel369.github.io")
print(f"  commit: {result.returncode} {result.stdout[:100]}")
result = subprocess.run(["git","push","origin","main"], capture_output=True, text=True,
               cwd=r"C:\Users\rmalk\projects\razel369.github.io")
print(f"  push: {result.returncode} {result.stderr[:200]}")
