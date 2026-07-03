#!/usr/bin/env python3
"""Look at existing owockibot submissions to see what to beat + look at owk-005 (security audit)."""
import json, subprocess, urllib.request, urllib.error, re

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(text)
        except: return e.code, text
    except Exception as e: return -1, str(e)

# 1) Look at owk-001 existing PRs
print("=" * 60)
print("OWK-001 (dashboard $750) - existing PRs")
print("=" * 60)
prs = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls?state=all&per_page=20")
if isinstance(prs, list):
    for p in prs[:10]:
        labels = [l.get("name","") for l in p.get("labels",[])]
        print(f"  #{p.get('number')} {p.get('state')} {p.get('title','')[:60]}")
        print(f"    files: {p.get('changed_files')}, +{p.get('additions')}/-{p.get('deletions')}")
        print(f"    user: {p.get('user',{}).get('login','?')}")

# 2) Look at owk-004 existing PRs
print()
print("=" * 60)
print("OWK-004 (badges $400) - existing PRs")
print("=" * 60)
prs = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls?state=all&per_page=20")
# Filter by title
if isinstance(prs, list):
    for p in prs:
        if "004" in p.get("title","") or "badge" in p.get("title","").lower():
            print(f"  #{p.get('number')} {p.get('state')} {p.get('title','')[:60]}")
            print(f"    user: {p.get('user',{}).get('login','?')}")
            print(f"    url: {p.get('html_url')}")

# 3) Look at owk-005 existing PRs
print()
print("=" * 60)
print("OWK-005 (security $1200) - existing PRs")
print("=" * 60)
if isinstance(prs, list):
    for p in prs:
        if "005" in p.get("title","") or "audit" in p.get("title","").lower() or "security" in p.get("title","").lower():
            print(f"  #{p.get('number')} {p.get('state')} {p.get('title','')[:60]}")
            print(f"    user: {p.get('user',{}).get('login','?')}")
            print(f"    url: {p.get('html_url')}")

# 4) Look at owockibot.xyz directly
print()
print("=" * 60)
print("OWOCKIBOT.XYZ (the actual platform)")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/")
if isinstance(d, str):
    print(f"  size: {len(d)}")
    # Find bounty IDs and links
    for m in re.finditer(r'/bounty/([a-zA-Z0-9_-]+)', d):
        print(f"  bounty: {m.group(0)}")
    # Find API endpoints
    for m in re.finditer(r'(/api/[a-zA-Z0-9_/-]+|owockibot\.xyz/[a-zA-Z0-9_/-]+)', d):
        print(f"  ref: {m.group(0)[:80]}")

# Look at specific bounty page
s, d = fetch("https://owockibot.xyz/bounty/owk-005")
if isinstance(d, str):
    print(f"\n  owk-005 page size: {len(d)}")
    # Extract body
    for m in re.finditer(r'<p[^>]*>([^<]+)</p>', d):
        text = m.group(1)[:200]
        if len(text) > 30:
            print(f"  text: {text[:200]}")

# 5) Get owk-004 details
print()
print("=" * 60)
print("OWK-004 (badges $400) - what sub-bounties?")
print("=" * 60)
s, d = fetch("https://owockibot.xyz/bounty/owk-004")
if isinstance(d, str):
    # Find body
    body_match = re.search(r'<div class="body[^>]*>(.+?)</div>', d, re.DOTALL)
    if body_match:
        body = re.sub(r'<[^>]+>', ' ', body_match.group(1))
        print(f"  body[:1500]: {body[:1500]}")

# 6) Get the owockibot API
print()
print("=" * 60)
print("OWOCKIBOT API")
print("=" * 60)
for path in ["/api/bounties", "/api/v1/bounties", "/api/bounty/owk-001", "/api/bounty/owk-004", "/api/bounty/owk-005", "/api/me/claims"]:
    for base in ["https://owockibot.xyz", "https://api.owockibot.xyz"]:
        s, d = fetch(f"{base}{path}")
        if s == 200:
            print(f"  {s} {base}{path}")
            if isinstance(d, (dict, list)):
                print(f"    {json.dumps(d)[:400]}")
