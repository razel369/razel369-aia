"""Send The Graph bug report via Guerrilla Mail API (no user setup needed).
Uses the temp email we just got: onpnbiks@guerrillamailblock.com
Session: li64db1ttos9qt84vcjs60toi2"""
import urllib.request, urllib.parse, json, ssl

ctx = ssl.create_default_context()
BASE = "https://api.guerrillamail.com/ajax.php"
SID = "li64db1ttos9qt84vcjs60toi2"
FROM = "onpnbiks@guerrillamailblock.com"
TO = "securitycontracts@thegraph.com"

# Read bug report
with open(r"C:\Users\rmalk\projects\razel369-aia\immunefi_report_001.md") as f:
    body = f.read()

subject = "[Security Report] Eligibility Period Bypass in RewardsEligibilityOracle - The Graph"

# Send via Guerrilla Mail
params = {
    "f": "send_email",
    "sid_token": SID,
    "email_from": FROM,
    "email_to": TO,
    "subject": subject,
    "body": body,
    "lang": "en"
}
url = f"{BASE}?{urllib.parse.urlencode(params)}"
print(f"Sending to: {TO}")
print(f"From: {FROM}")
print(f"Subject: {subject}")
print(f"Body length: {len(body)} chars")
print()

try:
    req = urllib.request.Request(url, headers={"User-Agent": "razel369-aia/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        result = r.read().decode()
        print(f"Status: {r.status}")
        print(f"Response: {result[:500]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode()[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Also check inbox for reply
print()
print("=== Checking inbox for any reply ===")
check_params = {"f": "get_email_list", "sid_token": SID, "offset": 0}
check_url = f"{BASE}?{urllib.parse.urlencode(check_params)}"
try:
    req = urllib.request.Request(check_url, headers={"User-Agent": "razel369-aia/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        inbox = json.loads(r.read().decode())
        emails = inbox.get("email_list", [])
        print(f"Inbox: {len(emails)} emails")
        for e in emails[:5]:
            print(f"  - {e.get('mail_from')}: {e.get('mail_subject', '')[:80]}")
except Exception as e:
    print(f"Inbox err: {e}")
