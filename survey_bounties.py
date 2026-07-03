#!/usr/bin/env python3
"""Survey real bug bounty programs. Find the best targets."""
import os, json, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
}

def call(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode()
    except Exception as e:
        return f"ERR: {e}"

# ============================================================
# 1) Get all Immunefi programs with details
# ============================================================
print("=" * 70)
print("1) IMMUNEFI — top programs sorted by max bounty")
print("=" * 70)

# The explore page returns a list
text = call("https://r.jina.ai/https://immunefi.com/explore?filter=active&maxBounty=100000")
# Extract programs
import re
# Find program names + max bounty from the page
programs = re.findall(r'(\w+(?:\s\w+)*)\s+(?:\$[\d.]+[KMB]?)\s+([\d.]+[KMB]?)?', text)
# Better: extract the table
table_match = re.search(r'\|.*?\|.*?\|.*?\|.*?\|(.*?)(?:Showing all|###)', text, re.DOTALL)
if table_match:
    rows = re.findall(r'\[(?:Image [^\]]*\])?\s*([^\]]+)\]\([^)]+\)[^|]*\|[^|]*\|[^|]*\$([\d.KM]+)', table_match.group(1))
    print(f"  found {len(rows)} rows")
    for name, max_b in rows[:20]:
        print(f"    {name.strip()}: ${max_b}")

# Alternative: pull from the JSON data embedded
# Look for programs that have "KYC Not Required" in their info
print()
print("Programs with KYC NOT REQUIRED (no paperwork to get paid):")
text2 = call("https://immunefi.com/explore?filter=active&kycNotRequired=true")
kyc_program_count = text2.count("KYC Not Required")
print(f"  Programs with KYC Not Required marker: {kyc_program_count} mentions in page")

# ============================================================
# 2) Look at specific high-value programs
# ============================================================
print()
print("=" * 70)
print("2) SPECIFIC PROGRAMS - check KYC + PoC requirements")
print("=" * 70)

programs_to_check = [
    ("ethena", "Ethena ($3M max)"),
    ("lombard-finance", "Lombard Finance ($250K)"),
    ("thegraph", "The Graph ($50K)"),
    ("ssvnetwork", "SSV Network ($250K)"),
    ("ens", "ENS ($250K)"),
    ("dexeprotocol", "DeXe ($500K)"),
    ("hedera", "Hedera ($30K)"),
]

for slug, desc in programs_to_check:
    print(f"\n  {desc}:")
    text = call(f"https://r.jina.ai/https://immunefi.com/bug-bounty/{slug}/information")
    # Look for key facts
    for keyword in ["KYC", "Safe Harbor", "PoC", "Max Bounty", "out of scope", "in scope", "asset", "token", "payout", "USDC", "payment"]:
        # Find sentences with this keyword
        matches = [line for line in text.split('\n') if keyword.lower() in line.lower() and len(line) < 300]
        if matches:
            for m in matches[:2]:
                print(f"    [{keyword}] {m.strip()[:200]}")

# ============================================================
# 3) Find the BIGGEST recent payouts to validate they pay
# ============================================================
print()
print("=" * 70)
print("3) RECENT PAYOUTS - proof they pay")
print("=" * 70)

text = call("https://r.jina.ai/https://immunefi.com/leaderboard")
print(text[:3000])
