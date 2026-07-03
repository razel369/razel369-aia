import socket, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dns.resolver

try:
    answers = dns.resolver.resolve("thegraph.com", "MX")
    for a in answers:
        print(f"MX: {a.exchange} priority={a.preference}")
except Exception as e:
    print(f"DNS err: {e}")

# Try Google DNS directly
import urllib.request
try:
    url = "https://dns.google/resolve?name=thegraph.com&type=MX"
    req = urllib.request.Request(url, headers={"User-Agent": "test"})
    with urllib.request.urlopen(req, timeout=15) as r:
        import json
        data = json.loads(r.read().decode())
        for a in data.get("Answer", []):
            print(f"  {a.get('name')} MX: {a.get('data')}")
except Exception as e:
    print(f"google dns err: {e}")
