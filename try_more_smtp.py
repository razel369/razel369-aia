import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid

# Read body
with open(r"C:\Users\rmalk\projects\razel369-aia\immunefi_report_001.md") as f:
    body = f.read()

sender = "razel369@protonmail.com"
to = "security@thegraph.com"
subject = "[Security Report] Eligibility Period Bypass in RewardsEligibilityOracle"

msg = MIMEText(body, "plain")
msg["From"] = sender
msg["To"] = to
msg["Subject"] = subject
msg["Date"] = formatdate(localtime=True)
msg["Message-ID"] = make_msgid(domain="protonmail.com")

# ProtonMail SMTP
print("Trying ProtonMail SMTP...")
try:
    s = smtplib.SMTP("smtp.protonmail.com", 587, timeout=15)
    s.ehlo()
    s.starttls()
    print("  TLS started")
    # No auth - we want to test if it accepts unauth
    code, msg_r = s.mail(sender)
    print(f"  MAIL FROM: {code} {msg_r[:80]}")
    code, msg_r = s.rcpt(to)
    print(f"  RCPT TO: {code} {msg_r[:80]}")
    code, msg_r = s.data(msg.as_bytes())
    print(f"  DATA: {code} {msg_r[:200]}")
    s.quit()
except Exception as e:
    print(f"  ERR: {e}")

print()
print("Trying SMTP.com free...")
try:
    s = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
    s.ehlo()
    s.starttls()
    s.mail(sender)
    s.rcpt(to)
    s.data(msg.as_bytes())
    s.quit()
    print("  ok")
except Exception as e:
    print(f"  ERR: {e}")
