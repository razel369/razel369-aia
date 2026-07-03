#!/usr/bin/env python3
"""Fix contributors.html encoding (UTF-16 LE -> UTF-8) and re-push to PR."""
import os, subprocess, sys

# 1) Read as UTF-16 LE
contrib_path = r"C:\Users\rmalk\projects\AgentPipe\contributors.html"
with open(contrib_path, "rb") as f:
    raw = f.read()
print(f"original size: {len(raw)}")
print(f"first 20 bytes: {raw[:20].hex()}")

# Detect encoding
if raw[:2] == b"\xff\xfe":
    text = raw.decode("utf-16-le")
    print(f"  -> UTF-16 LE, decoded {len(text)} chars")
elif raw[:3] == b"\xef\xbb\xbf":
    text = raw[3:].decode("utf-8")
    print(f"  -> UTF-8 with BOM, decoded {len(text)} chars")
else:
    try:
        text = raw.decode("utf-8")
        print(f"  -> UTF-8, decoded {len(text)} chars")
    except:
        text = raw.decode("utf-16-le")
        print(f"  -> UTF-16 LE fallback, decoded {len(text)} chars")

# Write back as UTF-8 (no BOM)
with open(contrib_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print(f"rewrote as UTF-8: {os.path.getsize(contrib_path)} bytes")

# 2) Show the actual content
print()
print("First 1500 chars of HTML:")
print(text[:1500])
print()
print(f"  has 71: {'71' in text}")
import re
print(f"  count of '71': {len(re.findall(r'71', text))}")
print(f"  has goose: {'goose' in text.lower()}")
print(f"  has golden egg: {'golden egg' in text.lower()}")
print(f"  has easter egg: {'easter' in text.lower()}")
print(f"  has factory: {'factor' in text.lower()}")

# 3) Git commit + push
print()
print("=" * 60)
print("GIT: commit + push")
print("=" * 60)
r = subprocess.run(["git","-C",r"C:\Users\rmalk\projects\AgentPipe","status"],
                   capture_output=True, text=True, timeout=30)
print(f"  status: {r.stdout[:500]}")
