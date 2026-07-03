#!/usr/bin/env python3
"""Debug BOM source."""
BOM = b'\xef\xbb\xbf'
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\devto.key", "rb") as f:
    raw_key = f.read()
print(f"key bytes (first 50): {raw_key[:50]}")
print(f"key has BOM: {raw_key[:3] == BOM}")

with open(r"C:\Users\rmalk\projects\razel369-aia\runx_love_post.md", "rb") as f:
    raw = f.read()
print(f"post bytes (first 50): {raw[:50]}")
print(f"post has BOM: {raw[:3] == BOM}")
print(f"total embedded BOMs: {raw.count(BOM)}")
