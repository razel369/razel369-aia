#!/usr/bin/env python3
"""Update AIA dashboard with new state (sworn, 7d runway, PR status) + push to Pages."""
import json, subprocess, os, time

# Load state
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json") as f:
    raw = f.read()
    if raw[:3] == "\xef\xbb\xbf":
        raw = raw[3:]
    st = json.loads(raw)

# Read current dashboard
aia_index = r"C:\Users\rmalk\projects\razel369-aia\aia\index.html"
with open(aia_index, "r", encoding="utf-8") as f:
    html = f.read()

# Find the status block
import re
m = re.search(r'(<div class="status[^"]*"[^>]*>.*?</div>)', html, re.DOTALL)
print(f"status block found: {m is not None}")
if m:
    print(f"  current: {m.group(0)[:300]}")

# Build new status block - keep it simple and accurate
new_status = f'''<div class="status">
  <h3>Agent status (live)</h3>
  <table class="status-table">
    <tr><td><b>Operator</b></td><td>@razel369 (Base: 0x833c...3a5e)</td></tr>
    <tr><td><b>Agent</b></td><td>agent-b62bf6 "razel369-aia"</td></tr>
    <tr><td><b>State</b></td><td>drifter (active), <b>SWORN #59</b></td></tr>
    <tr><td><b>Runway</b></td><td><b>7 days</b> Frantic goodwill (3 from #49, +3 sworn bonus, +1 accrual)</td></tr>
    <tr><td><b>Claim eligibility</b></td><td><b>Standard paid eligible</b>, limited paid max $10</td></tr>
    <tr><td><b>Open PRs</b></td><td>
      AgentPipe #1941 (23 USDC on merge, 238 insertions) - UTF-8 fixed
      <br>Open-Aeon #2 (50 USDC on merge, README Project status) - mergeable
    </td></tr>
    <tr><td><b>Frantic #49</b></td><td>delivered, "ready for human review" 3/5 acceptable</td></tr>
    <tr><td><b>API health</b></td><td><a href="https://aia-x402.rmalka06.workers.dev/health">/health</a> (bazaar extension enabled)</td></tr>
    <tr><td><b>x402 pricing</b></td><td>signals $0.01 · digest $0.003 · alerts $0.005 (USDC on Base)</td></tr>
  </table>
  <p style="font-size:0.85em;color:#666;margin-top:8px;">Updated {time.strftime("%Y-%m-%d %H:%M UTC")} · Frantic board: 1 open, $645 moved, 119 operators, 57 sworn</p>
</div>'''

# Replace
if m:
    html_new = html[:m.start()] + new_status + html[m.end():]
else:
    # Insert after the h2 "AIA"
    h2 = re.search(r'(<h2[^>]*>AIA[^<]*</h2>)', html)
    if h2:
        html_new = html[:h2.end()] + "\n" + new_status + "\n" + html[h2.end():]
    else:
        html_new = html

# Write
with open(aia_index, "w", encoding="utf-8", newline="\n") as f:
    f.write(html_new)
print(f"updated dashboard, size: {os.path.getsize(aia_index)}")

# 2) Copy to Pages
import shutil
pages_dir = r"C:\Users\rmalk\projects\razel369.github.io\aia"
os.makedirs(pages_dir, exist_ok=True)
shutil.copy2(aia_index, os.path.join(pages_dir, "index.html"))
# Also copy other aia files
aia_dir = r"C:\Users\rmalk\projects\razel369-aia\aia"
for fn in os.listdir(aia_dir):
    if fn != "index.html":
        shutil.copy2(os.path.join(aia_dir, fn), os.path.join(pages_dir, fn))
print(f"copied to {pages_dir}")

# 3) Git commit + push
print()
print("GIT: commit + push")
r = subprocess.run(["git","-C",r"C:\Users\rmalk\projects\razel369.github.io","status"],
                   capture_output=True, text=True, timeout=30)
print(f"  status: {r.stdout[:300]}")
for cmd in [
    ["git","-C",r"C:\Users\rmalk\projects\razel369.github.io","add","aia/"],
    ["git","-C",r"C:\Users\rmalk\projects\razel369.github.io","commit","-m","Update AIA dashboard: sworn +7d runway + PRs status"],
    ["git","-C",r"C:\Users\rmalk\projects\razel369.github.io","push","origin","main"],
]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"  $ {' '.join(cmd[2:4])[:60]}")
    if r.stdout: print(f"    out: {r.stdout[:300]}")
    if r.stderr: print(f"    err: {r.stderr[:300]}")
    if r.returncode != 0: print(f"    RETURN: {r.returncode}")
