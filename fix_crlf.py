#!/usr/bin/env python3
"""Fix line endings to CRLF (Windows default) for contributors.html + check GH status."""
import os, re, subprocess, json

contrib_path = r"C:\Users\rmalk\projects\AgentPipe\contributors.html"
with open(contrib_path, "r", encoding="utf-8") as f:
    text = f.read()

# Convert LF to CRLF
text_crlf = text.replace("\r\n", "\n").replace("\n", "\r\n")
print(f"LF count: {text.count(chr(10))}, CRLF count after: {text_crlf.count(chr(13)+chr(10))}")

with open(contrib_path, "wb") as f:
    f.write(text_crlf.encode("utf-8"))
print(f"size: {os.path.getsize(contrib_path)} bytes")

# Verify
BOM_BYTES = b"\xef\xbb\xbf"
CRLF_BYTES = b"\r\n"
with open(contrib_path, "rb") as f:
    raw = f.read()
print(f"  first 20 bytes: {raw[:20]}")
print(f"  no BOM: {raw[:3] != BOM_BYTES}")
print(f"  has CRLF: {CRLF_BYTES in raw[:1000]}")

# Git operations
print()
print("GIT: add, commit, push")
for cmd in [
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","status"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","add","contributors.html"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","diff","--cached","--stat"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","commit","-m","Force CRLF line endings in contributors.html so GitHub shows it as text"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","push","origin","contributors-page-1938","--force-with-lease"],
]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"  $ {' '.join(cmd[2:4])[:60]}")
    if r.stdout: print(f"    out: {r.stdout[:400]}")
    if r.stderr: print(f"    err: {r.stderr[:400]}")
    if r.returncode != 0: print(f"    RETURN: {r.returncode}")
