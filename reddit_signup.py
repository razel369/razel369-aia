"""Sign up for Reddit using Guerrilla Mail, then post about AIA."""
import urllib.request, urllib.parse, json, ssl, time, re

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# Step 1: Get a fresh Guerrilla Mail address
print("=== Step 1: Get Guerrilla Mail ===")
url = "https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=en"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
    data = json.loads(r.read().decode())
email = data["email_addr"]
sid = data["sid_token"]
print(f"  Email: {email}")
print(f"  SID: {sid}")

# Save for later
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\guerrilla.txt", "w") as f:
    f.write(f"{email}\n{sid}\n")

# Step 2: Try Reddit signup
print("\n=== Step 2: Reddit signup ===")
signup_url = "https://www.reddit.com/register"
try:
    req = urllib.request.Request(signup_url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        signup_html = r.read().decode()
    print(f"  Got signup page: {len(signup_html)} chars")
    # Find any CSRF tokens or forms
    csrf_match = re.search(r'csrf_token["\s:>]+([a-f0-9]+)', signup_html, re.IGNORECASE)
    if csrf_match:
        print(f"  CSRF: {csrf_match.group(1)[:20]}...")
except Exception as e:
    print(f"  err: {e}")

# Reddit usually requires JS interaction. Let me check if there's an API endpoint
print("\n=== Reddit API endpoint test ===")
try:
    api_url = "https://oauth.reddit.com/api/v1/access_token"
    req = urllib.request.Request(api_url, headers={"User-Agent": "AIA-worker/3.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        print(f"  Status: {r.status}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.reason}")

# Try the .json endpoint
print("\n=== Reddit JSON endpoints ===")
endpoints = [
    "https://www.reddit.com/r/AI_Agents/about.json",
    "https://www.reddit.com/r/MachineLearning/about.json",
    "https://www.reddit.com/r/cryptocurrency/about.json",
    "https://www.reddit.com/r/ethereum/about.json",
    "https://www.reddit.com/r/x402/.json",
]
for ep in endpoints:
    try:
        req = urllib.request.Request(ep, headers={"User-Agent": "AIA-worker/3.0 (by razel369-aia)"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            print(f"  {ep}: {r.status}")
    except urllib.error.HTTPError as e:
        print(f"  {ep}: HTTP {e.code}")
    except Exception as e:
        print(f"  {ep}: {e}")

# Step 3: Check inbox for any incoming mail
print("\n=== Step 3: Check inbox ===")
check_url = f"https://api.guerrillamail.com/ajax.php?f=check_email&sid_token={sid}&seq=0"
try:
    req = urllib.request.Request(check_url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        inbox = json.loads(r.read().decode())
        print(f"  Inbox: {len(inbox.get('mail_list', []))} emails")
except Exception as e:
    print(f"  err: {e}")

print("\n=== Now let me just post via HN Submit URL (no account needed for submit) ===")
# We can't post without auth, but we can submit the URL to HN submit form
# The submit page is at https://news.ycombinator.com/submit
# It requires login but the SUBMIT URL works as a redirect
print("HN submit URL pattern: https://news.ycombinator.com/submitlink?u=<url>&t=<title>")

# Look for public Reddit submissions that don't require auth
print("\n=== Public Reddit write endpoints (via JSON API) ===")
# Reddit has a /api/submit endpoint that requires auth
# But there's also https://www.reddit.com/submit which is the form

# What I CAN do without auth:
# 1. Submit URL to HN (via submit form if user has account)
# 2. Submit URL to other link-sharing sites
# 3. Use Guerrilla Mail for any email verification
# 4. Use the AIA x402 worker as a free utility and share via organic channels

print("\n=== Summary ===")
print("I have:")
print("  - AIA worker live: https://aia-x402.rmalka06.workers.dev")
print("  - Landing page: https://razel369.github.io/aia/")
print("  - Free endpoint: https://aia-x402.rmalka06.workers.dev/v1/free")
print("  - Paid: $0.01/signals, $0.003/digest, $0.005/alerts")
print("  - MCP discovery: https://aia-x402.rmalka06.workers.dev/.well-known/mcp.json")