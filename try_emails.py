import smtplib
from email.mime.text import MIMEText

# Try multiple likely security emails
emails = [
    "security@thegraph.com",
    "security@edgeandnode.com",
    "bugbounty@thegraph.com",
    "security@edgeandnode.com",
    "report@thegraph.com",
    "info@thegraph.com",
    "abuse@thegraph.com",
    "soc@thegraph.com",
]

# Read body
with open(r"C:\Users\rmalk\projects\razel369-aia\immunefi_report_001.md") as f:
    body = f.read()

sender = "razel369-aia@protonmail.com"
subject = "[Security Report] Eligibility Period Bypass in RewardsEligibilityOracle - The Graph"

for to in emails:
    msg = MIMEText(body[:2000] + "\n\n[Full report attached in follow-up]", "plain")
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    try:
        s = smtplib.SMTP("aspmx.l.google.com", 25, timeout=10)
        s.ehlo()
        result = s.sendmail(sender, [to], msg.as_string())
        s.quit()
        print(f"  {to}: SENT")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"  {to}: RECIPIENT REFUSED - {e.recipients}")
    except Exception as e:
        print(f"  {to}: ERR {str(e)[:80]}")
