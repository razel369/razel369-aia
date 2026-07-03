#!/usr/bin/env python3
"""Use Jina search via API (needs key, but search.jina.ai is free)."""
import os, re, json, urllib.request, ssl
from urllib.parse import quote

ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/plain",
}

def jina_search(q):
    """Search via s.jina.ai — needs the search subdomain."""
    url = f"https://s.jina.ai/{quote(q)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return f"ERR: {e}"

def jina_read(url):
    """Read URL via r.jina.ai"""
    url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return f"ERR: {e}"

# Try DuckDuckGo HTML (no API key needed)
def ddg(q):
    url = f"https://html.duckduckgo.com/html/?q={quote(q)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return f"ERR: {e}"

print("=" * 70)
print("DDG SEARCH 1: agent marketplaces")
print("=" * 70)
text = ddg("AI agent marketplace USDC 2026 list earn autonomous paid tasks")
# Extract results
urls = re.findall(r'href="(https?://[^"]+)"', text)
real_urls = [u for u in urls if "duckduckgo" not in u and "duck.com" not in u and ".css" not in u and ".js" not in u and ".png" not in u]
print(f"Found {len(set(real_urls))} unique URLs")
for u in list(set(real_urls))[:30]:
    print(f"  - {u}")

print()
print("=" * 70)
print("DDG SEARCH 2: x402 paid APIs")
print("=" * 70)
text = ddg("x402 paid API marketplace 2026 agent pay per call USDC")
urls = re.findall(r'href="(https?://[^"]+)"', text)
real_urls = [u for u in urls if "duckduckgo" not in u and "duck.com" not in u and ".css" not in u and ".js" not in u and ".png" not in u]
print(f"Found {len(set(real_urls))} unique URLs")
for u in list(set(real_urls))[:30]:
    print(f"  - {u}")

print()
print("=" * 70)
print("DDG SEARCH 3: AI agent bounties")
print("=" * 70)
text = ddg("AI agent bounty board 2026 paid USDC crypto")
urls = re.findall(r'href="(https?://[^"]+)"', text)
real_urls = [u for u in urls if "duckduckgo" not in u and "duck.com" not in u and ".css" not in u and ".js" not in u and ".png" not in u]
print(f"Found {len(set(real_urls))} unique URLs")
for u in list(set(real_urls))[:30]:
    print(f"  - {u}")
