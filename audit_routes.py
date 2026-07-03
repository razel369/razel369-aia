#!/usr/bin/env python3
"""Look at submit + claim routes + signature verification + look at /agents POST."""
import re

with open(r"C:\Users\rmalk\projects\razel369-aia\server_full.js", "r", encoding="utf-8") as f:
    content = f.read()
lines = content.split("\n")

# Look at submit, claim, /agents POST routes
for start, end, name in [
    (560, 620, "/agents POST"),
    (617, 680, "/webhooks POST"),
    (1286, 1370, "/bounties/:id/claim"),
    (1367, 1505, "/bounties/:id/submit"),
]:
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    for i in range(start, min(end, len(lines))):
        print(f"  {i+1:5d}: {lines[i]}")
