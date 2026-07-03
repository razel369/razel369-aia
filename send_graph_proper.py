"""Send The Graph security bug report - properly formatted to avoid spam filters."""
import smtplib, uuid, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

# Read bug report
with open(r"C:\Users\rmalk\projects\razel369-aia\immunefi_report_001.md") as f:
    body = f.read()

sender_email = "security-reports@razel369-aia.dev"
sender_name = "Razel Security Research"
to = "security@thegraph.com"
subject = "[Security Report] Eligibility Period Bypass in RewardsEligibilityOracle - The Graph"

# Build proper MIME message
msg = MIMEMultipart("alternative")
msg["From"] = f"{sender_name} <{sender_email}>"
msg["To"] = to
msg["Subject"] = subject
msg["Date"] = formatdate(localtime=True)
msg["Message-ID"] = make_msgid(domain="razel369-aia.dev")
msg["Reply-To"] = "razel369@protonmail.com"
msg["X-Mailer"] = "razel369-aia/1.0"

# Plain text version
text_part = MIMEText(body, "plain", "utf-8")
msg.attach(text_part)

print(f"From: {msg['From']}")
print(f"To: {to}")
print(f"Subject: {msg['Subject']}")
print(f"Message-ID: {msg['Message-ID']}")
print(f"Date: {msg['Date']}")
print(f"Body: {len(body)} chars")
print()

# Try multiple MX servers with backoff
import socket
socket.setdefaulttimeout(15)

mx_list = [
    ("aspmx.l.google.com", 25),
    ("alt1.aspmx.l.google.com", 25),
    ("alt2.aspmx.l.google.com", 25),
]

for host, port in mx_list:
    for attempt in range(3):
        try:
            print(f"Attempt {attempt+1}: {host}:{port}...")
            s = smtplib.SMTP(host, port, timeout=20)
            s.set_debuglevel(0)
            code, msg_resp = s.ehlo("razel369-aia.dev")
            print(f"  EHLO: {code} {msg_resp[:80]}")
            code, msg_resp = s.mail(sender_email)
            print(f"  MAIL FROM: {code} {msg_resp[:80]}")
            code, msg_resp = s.rcpt(to)
            print(f"  RCPT TO: {code} {msg_resp[:80]}")
            code, msg_resp = s.data(msg.as_bytes())
            print(f"  DATA: {code} {msg_resp[:200]}")
            s.quit()
            print(f"\n  *** SENT via {host} ***")
            break
        except smtplib.SMTPRecipientsRefused as e:
            print(f"  RECIPIENT REFUSED: {e.recipients}")
            break
        except Exception as e:
            print(f"  ERR: {e}")
            time.sleep(2)
            continue
        break
