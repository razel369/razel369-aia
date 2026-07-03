#!/usr/bin/env python3
"""Email the security contact at The Graph and also try to register on Immunefi."""
import os, urllib.request, urllib.error, ssl, json

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
}

# 1) Try to create Immunefi account
print("=" * 70)
print("1) IMMUNEFI REGISTRATION")
print("=" * 70)

# Get the signup page
req = urllib.request.Request("https://bugs.immunefi.com/signup", headers=HEADERS)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        body = r.read().decode()
        print(f"  status: {r.status}, {len(body)}b")
        # Look for CSRF token
        import re
        csrf = re.search(r'name="authenticity_token"\s+value="([^"]+)"', body)
        if csrf:
            print(f"  CSRF token found: {csrf.group(1)[:30]}")
        # Or any hidden form fields
        for m in re.finditer(r'<input[^>]+type="hidden"[^>]+>', body):
            print(f"  hidden: {m.group(0)[:200]}")
except Exception as e:
    print(f"  ERR: {e}")

# 2) Email The Graph security contact via Gmail API would need OAuth
# But we can prepare a mailto link
print()
print("=" * 70)
print("2) EMAIL LINK for The Graph security team")
print("=" * 70)

import os
with open("C:/Users/rmalk/projects/razel369-aia/immunefi_report_001.md") as f:
    report = f.read()

# Save to a format that can be pasted
print(f"  Report: {len(report)} chars")
print()
print("  Email recipient: security+contracts@thegraph.com")
print("  (remove the space the team added in the contract comment)")
print()
print("  Open the report at:")
print(f"  file:///C:/Users/rmalk/projects/razel369-aia/immunefi_report_001.md")
print()
print("  Suggested subject: 'Security finding — RewardsEligibilityOracle eligibility bypass'")

# 3) Save a copy of the report in plain text for easy email
with open("C:/Users/rmalk/projects/razel369-aia/immunefi_report_001.txt", "w") as f:
    f.write(report)
print("  Also saved as .txt for easy paste into email")

# 4) Try to open default email client
import subprocess
# Create a mailto URL
mailto = f"mailto:securitycontracts@thegraph.com?subject=Security%20finding%20%E2%80%94%20RewardsEligibilityOracle%20eligibility%20bypass&body={urllib.parse.quote(report[:1000])}"
try:
    subprocess.run(f'start "" "{mailto}"', shell=True, timeout=10)
    print()
    print("  ✓ Opened default email client with the report pre-filled")
except:
    print()
    print(f"  Email URL: {mailto}")
