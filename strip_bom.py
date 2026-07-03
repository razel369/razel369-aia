#!/usr/bin/env python3
"""Strip BOM from contributors.html and force re-push."""
import os, subprocess

contrib_path = r"C:\Users\rmalk\projects\AgentPipe\contributors.html"
BOM = b"\xef\xbb\xbf"

with open(contrib_path, "rb") as f:
    raw = f.read()
print(f"size: {len(raw)}, starts with BOM: {raw[:3] == BOM}")

# Strip BOM
if raw[:3] == BOM:
    raw = raw[3:]
    with open(contrib_path, "wb") as f:
        f.write(raw)
    print(f"stripped BOM, new size: {len(raw)}")
else:
    print("no BOM to strip")

# Verify
with open(contrib_path, "rb") as f:
    raw2 = f.read()
print(f"verified: starts with BOM: {raw2[:3] == BOM}, first 20: {raw2[:20]}")

# Git: remove, add, force push
print()
print("GIT: force text add + push")
for cmd in [
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","rm","--cached","contributors.html"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","add","contributors.html"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","status"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","diff","--cached","--stat","--no-renames"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","commit","-m","Strip UTF-8 BOM from contributors.html and ensure CRLF"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","push","origin","contributors-page-1938","--force-with-lease"],
]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"  $ {' '.join(cmd[2:4])[:60]}")
    if r.stdout: print(f"    out: {r.stdout[:400]}")
    if r.stderr: print(f"    err: {r.stderr[:400]}")
    if r.returncode != 0: print(f"    RETURN: {r.returncode}")
