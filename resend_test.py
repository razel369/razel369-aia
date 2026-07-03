import urllib.request, urllib.parse, json
# Resend free tier - 100 emails/day, 3000/month
# Need API key but let me try the test mode first

# Check if they have a public test endpoint
urls = [
    "https://api.resend.com/health",
    "https://resend.com/api/health",
    "https://api.resend.com/v1/health",
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "test"})
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"{url}: {r.status} {r.read().decode()[:200]}")
    except Exception as e:
        print(f"{url}: {str(e)[:80]}")
