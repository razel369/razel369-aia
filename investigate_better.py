#!/usr/bin/env python3
"""Look at maintainer's profile, find SUBMISSION_GUIDELINES, find other real bounty platforms."""
import os, json, urllib.request, ssl, urllib.error, subprocess

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
}

def call(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode()
    except Exception as e:
        return f"ERR: {e}"

# 1) Maintainer profile
print("=" * 70)
print("1) MAINTAINER PROFILE")
print("=" * 70)
r = subprocess.run(["gh","api","users/cyrilawoyemi99-max"], capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    j = json.loads(r.stdout)
    print(f"  name: {j.get('name')}")
    print(f"  login: {j.get('login')}")
    print(f"  bio: {j.get('bio')}")
    print(f"  company: {j.get('company')}")
    print(f"  blog: {j.get('blog')}")
    print(f"  twitter: {j.get('twitter_username')}")
    print(f"  location: {j.get('location')}")
    print(f"  email: {j.get('email')}")
    print(f"  public_repos: {j.get('public_repos')}")
    print(f"  created_at: {j.get('created_at')}")
    print(f"  followers: {j.get('followers')}")
    print(f"  following: {j.get('following')}")

# 2) Other repos by maintainer
print()
print("=" * 70)
print("2) MAINTAINER'S OTHER REPOS")
print("=" * 70)
r = subprocess.run(["gh","api","users/cyrilawoyemi99-max/repos?per_page=20"],
                   capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    repos = json.loads(r.stdout)
    for repo in repos[:15]:
        print(f"  {repo.get('name')}: {repo.get('description','')[:80]}")
        print(f"    stars: {repo.get('stargazers_count')}, fork: {repo.get('fork')}, updated: {repo.get('updated_at')}")

# 3) Look for SUBMISSION_GUIDELINES in fork
print()
print("=" * 70)
print("3) SUBMISSION_GUIDELINES.md")
print("=" * 70)
text = call("https://r.jina.ai/https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/blob/main/SUBMISSION_GUIDELINES.md")
print(text[:3000])

# 4) Find other bounty boards
print()
print("=" * 70)
print("4) SEARCH FOR OTHER BOUNTY BOARDS")
print("=" * 70)

# Search GitHub
for query in ["bounty board USDC base", "bounty agent USDC x402", "paid bounty agent base"]:
    r = subprocess.run(["gh","search","repos",query,"--sort","stars","--limit","10"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        # Parse output
        lines = r.stdout.strip().split("\n")
        print(f"  query: {query}")
        for line in lines[:7]:
            print(f"    {line[:120]}")
        print()
