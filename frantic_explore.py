#!/usr/bin/env python3
"""Explore Frantic MCP + extract all bounties + recreate #1938 path."""
import json, urllib.request, urllib.error, re, base64

def fetch(url, headers=None):
    h = {"User-Agent":"razel369-aia/1.0"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", errors="replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500], dict(e.headers) if hasattr(e,"headers") else {}
    except Exception as e:
        return -1, str(e), {}

# 1) Frantic MCP manifest
print("=" * 60)
print("Frantic MCP manifest")
print("=" * 60)
s, body, h = fetch("https://api.gofrantic.com/mcp.json", {"Accept":"application/json"})
print(f"status: {s}, size: {len(body)}")
if s == 200:
    try:
        m = json.loads(body)
        print(json.dumps(m, indent=2)[:3000])
    except:
        print(body[:2000])

# 2) Frantic homepage bounties extraction
print()
print("=" * 60)
print("Frantic homepage bounties (extract from HTML)")
print("=" * 60)
s, body, _ = fetch("https://gofrantic.com")
# Find all bounty links
ids = list(set(re.findall(r'https://gofrantic\.com/bounties/(p-[a-f0-9]+)', body)))
print(f"Bounty IDs found: {ids}")
# Find names
text = re.sub(r"<[^>]+>"," ",body)
text = re.sub(r"\s+"," ",text)
for kw in ["bounty", "Give runx", "love", "reward", "ETH", "paid"]:
    for m in re.finditer(kw, text, re.IGNORECASE):
        start = max(0, m.start()-50)
        end = min(len(text), m.end()+200)
        print(f"  '{kw}': ...{text[start:end]}...")
        break

# 3) Visit each bounty page
print()
print("=" * 60)
print("Frantic bounties detail")
print("=" * 60)
for bid in ids[:5]:
    s, body, _ = fetch(f"https://gofrantic.com/bounties/{bid}")
    if s == 200:
        # Extract description, reward, requirements
        title_m = re.search(r'<title>([^<]+)</title>', body)
        og_m = re.search(r'property="og:description"\s+content="([^"]+)"', body)
        text = re.sub(r"<[^>]+>"," ",body)
        text = re.sub(r"\s+"," ",text)
        # Look for reward/value/skills
        print(f"\n  === {bid} ===")
        if title_m: print(f"  title: {title_m.group(1)[:100]}")
        if og_m: print(f"  og: {og_m.group(1)[:300]}")
        # First 800 chars of text
        print(f"  text: {text[:1500]}")

# 4) auscaster/frantic-board README + RULES
print()
print("=" * 60)
print("frantic-board README + RULES")
print("=" * 60)
def gh_raw(path):
    return fetch(f"https://raw.githubusercontent.com/{path}", {"User-Agent":"razel369-aia/1.0"})

for f in ["auscaster/frantic-board/main/README.md", "auscaster/frantic-board/main/RULES.md", "auscaster/frantic-board/main/CONTRIBUTING.md"]:
    s, body, _ = gh_raw(f)
    print(f"\n  === {f} ===")
    if s == 200:
        print(body[:3000])
    else:
        print(f"  err: {s}")

# 5) runxhq/runx (Frantic's underlying platform)
print()
print("=" * 60)
print("runxhq/runx")
print("=" * 60)
for f in ["runxhq/runx/main/README.md"]:
    s, body, _ = gh_raw(f)
    print(f"  {f}: {s}, size {len(body)}")
    if s == 200:
        print(body[:2000])

# 6) Check Frantic API paths systematically
print()
print("=" * 60)
print("Frantic API systematic scan")
print("=" * 60)
for path in [
    "/v1/bounties", "/v1/agents", "/v1/board", "/v1/posts",
    "/bounties.json", "/agents.json", "/board.json",
    "/.well-known/mcp", "/.well-known/agent",
    "/skill.md", "/skill.json", "/AGENTS.md"
]:
    s, body, _ = fetch(f"https://api.gofrantic.com{path}")
    print(f"  {s:>3} {len(body):>6}b  api.gofrantic.com{path}")
