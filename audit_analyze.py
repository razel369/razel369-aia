#!/usr/bin/env python3
"""Read full server.js for owk-005 audit + check owockibot builder category + look for sub-bounties I can claim."""
import re, json, urllib.request, urllib.error, os

# 1) Read the saved server.js and look for vulnerabilities
print("=" * 60)
print("SERVER.JS VULNERABILITY ANALYSIS")
print("=" * 60)
with open(r"C:\Users\rmalk\projects\razel369-aia\server_full.js", "r", encoding="utf-8") as f:
    content = f.read()

# Find all route handlers with their bodies
print("Total chars:", len(content))
print()

# Look for specific vulnerability patterns
patterns = [
    (r"app\.post\(['\"](\/[^'\"]+)", "POST routes"),
    (r"app\.get\(['\"](\/[^'\"]+)", "GET routes"),
    (r"app\.delete\(['\"](\/[^'\"]+)", "DELETE routes"),
    (r"app\.put\(['\"](\/[^'\"]+)", "PUT routes"),
    (r"app\.patch\(['\"](\/[^'\"]+)", "PATCH routes"),
    (r"function\s+(\w+)\s*\([^)]*\)\s*\{", "Functions"),
]

# Look for auth bypass opportunities
print("Routes that DON'T check isMod or auth:")
lines = content.split("\n")
current_route = None
in_body = False
body_lines = []
issues = []
for i, line in enumerate(lines):
    m = re.search(r"app\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]", line)
    if m:
        if current_route and body_lines:
            body = "\n".join(body_lines)
            # Check for mod check
            has_mod = "isMod" in body or "MOD_WALLETS" in body or "requireSig" in body
            if not has_mod and current_route["method"] in ["POST", "PUT", "DELETE", "PATCH"]:
                issues.append((current_route, i, body[:200]))
        current_route = {"method": m.group(1).upper(), "path": m.group(2), "line": i}
        body_lines = []
    elif current_route and "});" in line:
        if current_route and body_lines:
            body = "\n".join(body_lines)
            has_mod = "isMod" in body or "MOD_WALLETS" in body or "requireSig" in body
            if not has_mod and current_route["method"] in ["POST", "PUT", "DELETE", "PATCH"]:
                issues.append((current_route, i, body[:200]))
        current_route = None
        body_lines = []
    elif current_route:
        body_lines.append(line)

print(f"  potential auth issues: {len(issues)}")
for route, line, body in issues[:15]:
    print(f"\n  {route['method']} {route['path']} (line {line}):")
    print(f"    {body[:300]}")

# Look for "owner" / "creator" checks
print()
print("=" * 60)
print("Routes that may have privilege issues:")
print("=" * 60)
# Check the approve/cancel/release routes
for kw in ["approve", "cancel", "release", "delete", "reject", "update", "patch", "create"]:
    for m in re.finditer(rf"app\.(post|put|delete|patch)\(['\"]([^'\"]*{kw}[^'\"]*)['\"]", content, re.IGNORECASE):
        print(f"    {m.group(1).upper()} {m.group(2)}")

# 2) Check owockibot builder category page
print()
print("=" * 60)
print("OWOCKIBOT.XYZ builder category")
print("=" * 60)
s, d = fetch_url("https://owockibot.xyz/builder")
if isinstance(d, str):
    print(f"  size: {len(d)}")
    # Find bounties
    bounty_ids = set()
    for m in re.finditer(r'/bounty/(\d+)', d):
        bounty_ids.add(int(m.group(1)))
    for m in re.finditer(r'\$(\d+)', d):
        pass
    print(f"  bounty IDs: {sorted(bounty_ids)}")
    # Find titles
    titles = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', d)
    for t in titles[:10]:
        print(f"    title: {t.strip()}")

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except Exception as e: return -1, str(e)

# 3) Check owockibot API for /api/builder or category endpoints
for path in ["/api/builder", "/api/category/builder", "/api/bounties?category=builder", "/api/v1/builder", "/api/bounties?status=open&category=builder"]:
    s, d = fetch_url(f"https://owockibot.xyz{path}")
    if s == 200:
        if isinstance(d, list):
            print(f"  {s} {path}: list({len(d)})")
            for b in d[:5]:
                print(f"    #{b.get('id')} ${b.get('reward_usdc')} [{b.get('status')}] {b.get('title','')[:60]}")
        elif isinstance(d, dict):
            print(f"  {s} {path}: {list(d.keys())[:5]}")
