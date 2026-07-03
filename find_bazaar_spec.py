#!/usr/bin/env python3
"""Get x402-bazaar spec, check agentic.market submission process, then update Worker."""
import json, urllib.request, urllib.error

# 1) Get the x402-bazaar spec
print("=" * 60)
print("1. x402-bazaar spec")
print("=" * 60)
for url in [
    "https://raw.githubusercontent.com/coinbase/x402/main/extensions/bazaar/README.md",
    "https://raw.githubusercontent.com/coinbase/x402/main/extensions/bazaar/bazaar.md",
    "https://raw.githubusercontent.com/coinbase/x402/main/extensions/bazaar/schema.json",
]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"razel369-aia/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            print(f"\n--- {url} ({len(body)} chars) ---")
            print(body[:3500])
    except Exception as e:
        print(f"\n--- {url} ERR: {e} ---")

# 2) Check x402 main README
print()
print("=" * 60)
print("2. x402 main repo - bazaar extension")
print("=" * 60)
try:
    req = urllib.request.Request("https://raw.githubusercontent.com/coinbase/x402/main/extensions/bazaar/extension.md",
                                 headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read().decode("utf-8")
        print(body[:3000])
except Exception as e:
    print(f"err: {e}")

# 3) Check how agentic.market is built - is there a GitHub repo?
print()
print("=" * 60)
print("3. Find agentic.market submission mechanism")
print("=" * 60)
# Try common URLs
for u in ["https://github.com/coinbase/agentic-market",
          "https://github.com/cdp/agentic-market",
          "https://github.com/agentic-market",
          "https://github.com/coinbase/x402/tree/main/agents"]:
    try:
        req = urllib.request.Request(u, headers={"User-Agent":"razel369-aia/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f"  {u} → {r.status}")
    except urllib.error.HTTPError as e:
        print(f"  {u} → {e.code}")
    except Exception as e:
        print(f"  {u} → err: {e}")

# 4) Look at the agentic.market HTML for submission hints
print()
print("=" * 60)
print("4. agentic.market home page submit hints")
print("=" * 60)
try:
    req = urllib.request.Request("https://agentic.market", headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read().decode("utf-8")
        # Find any submit / add / register hints
        import re
        for kw in ["submit","add your","list your","register","/.well-known"]:
            for m in re.finditer(kw, body, re.IGNORECASE):
                start = max(0, m.start()-100)
                end = min(len(body), m.end()+200)
                snippet = body[start:end].replace("\n"," ")
                print(f"  match '{kw}': ...{snippet}...")
                break
except Exception as e:
    print(f"err: {e}")
