import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender = "razel369-aia@protonmail.com"
to = "securitycontracts@thegraph.com"
subject = "[Security Report] Eligibility Period Bypass in RewardsEligibilityOracle - The Graph"

with open(r"C:\Users\rmalk\projects\razel369-aia\immunefi_report_001.md") as f:
    body = f.read()

msg = MIMEText(body, "plain")
msg["From"] = sender
msg["To"] = to
msg["Subject"] = subject

# Try common MX servers
mx_hosts = [
    "aspmx.l.google.com",
    "alt1.aspmx.l.google.com",
    "mx1.emailsrvr.com",
    "thegraph-com.mail.protection.outlook.com",
]

for host in mx_hosts:
    try:
        print(f"Trying {host}:25...")
        s = smtplib.SMTP(host, 25, timeout=10)
        s.ehlo()
        s.sendmail(sender, [to], msg.as_string())
        s.quit()
        print(f"  SUCCESS: {host}")
        break
    except Exception as e:
        print(f"  FAIL: {e}")
        continue
