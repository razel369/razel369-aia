#!/usr/bin/env python3
"""Find smaller, easier-to-audit Immunefi programs alongside The Graph.
Target: programs with $5K-$25K max bounty, smaller codebases, faster time-to-pay."""
import os, json, urllib.request, ssl, urllib.error, re

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/plain",
}

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode()
    except Exception as e:
        return f"ERR: {e}"

# 1) Get the list of all Immunefi programs with metrics
print("=" * 70)
print("ALL IMMUNEFI PROGRAMS — sort by ease of audit (paid > $0 + smaller)")
print("=" * 70)

# Use jina to get the explore page
text = fetch("https://r.jina.ai/https://immunefi.com/explore?filter=active")
# Extract program names + max bounty
# Format: | [icon] ProgramName | $TVL | $MaxBounty | $Paid | med time |

# Find program lines
import re
# Match program names with their data
matches = re.findall(r'\[!\[Image[^\]]+\]\s+([^\]]+)\]\(https://immunefi\.com/bug-bounty/([\w-]+)/information/\)\s*\|[^|]*\|\s*\$([0-9.]+[KMB]?)\s*\|\s*\$?([\w.]+[KMB]?|Private)', text)

print(f"  parsed {len(matches)} programs")
for name, slug, max_b, paid in matches[:30]:
    print(f"    {name.strip():30s} ${max_b:6s} | paid: {paid} | slug: {slug}")

# 2) Find programs with $5K-$50K bounty + already paid
print()
print("=" * 70)
print("FASTER-PAYING TARGETS — small bounty, already paid (proves they pay)")
print("=" * 70)

real_paid = [m for m in matches if m[3] not in ("Private", "0")]
real_paid.sort(key=lambda x: float(x[2].replace("K", "").replace("M", "").replace("B", "")) * (1 if "M" in x[2] else 0.001))
print(f"  programs with public payouts: {len(real_paid)}")
for name, slug, max_b, paid in real_paid[:20]:
    print(f"    {name.strip():30s} max ${max_b:6s}  paid: {paid}  → /{slug}")

# 3) Look at Lombard Finance specifically (newer, less audited, $250K)
print()
print("=" * 70)
print("LOMBARD FINANCE — newest + $250K max, less audited = easier to find bug")
print("=" * 70)
text = fetch("https://r.jina.ai/https://immunefi.com/bug-bounty/lombard-finance/scope")
print(text[:3000])

# 4) The Graph scope
print()
print("=" * 70)
print("THE GRAPH — explicit in-scope contracts")
print("=" * 70)
text = fetch("https://r.jina.ai/https://immunefi.com/bug-bounty/thegraph/scope")
# Look for in-scope list
print(text[:3000])
