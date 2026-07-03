import smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender = "razel369@protonmail.com"
to = "securitycontracts@thegraph.com"
subject = "[Security] Eligibility Period Bypass in The Graph RewardsEligibilityOracle"
body = open(r"C:\Users\rmalk\projects\razel369-aia\immunefi_report_001.md").read()

msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = to
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Try multiple MX records
import subprocess
mx = subprocess.check_output(["nslookup", "-type=mx", "thegraph.com"], text=True)
print("MX records:")
print(mx)
