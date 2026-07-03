#!/usr/bin/env python3
"""Look at specific server.js routes for vulnerabilities + check owockibot builder category."""
import re, json, urllib.request, urllib.error, os

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except Exception as e: return -1, str(e)

# 1) Read server.js and look at the specific vulnerable routes
print("=" * 60)
print("SERVER.JS - LOOK AT grade, release, cancel, approve, reject routes")
print("=" * 60)
with open(r"C:\Users\rmalk\projects\razel369-aia\server_full.js", "r", encoding="utf-8") as f:
    content = f.read()
lines = content.split("\n")

# Look at line 1967 (grade) and 2073 (release) and 2115 (cancel)
for start_line in [1967, 2073, 2115, 1563, 1867]:
    print(f"\n  --- ROUTE @ line {start_line} ---")
    end = min(start_line + 30, len(lines))
    for i in range(start_line - 1, end):
        print(f"  {i+1:5d}: {lines[i]}")
    print()

# Look at where modWallets are checked in approve
print()
print("  --- /bounties/:id/approve full route ---")
for i, line in enumerate(lines):
    if "bounties/:id/approve" in line and "app.post" in line:
        end = min(i + 70, len(lines))
        for j in range(i, end):
            print(f"  {j+1:5d}: {lines[j]}")
        break
