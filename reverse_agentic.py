#!/usr/bin/env python3
"""Reverse-engineer agentic.market submission: fetch one full service entry + look for endpoints."""
import json, urllib.request, urllib.error, re

# 1) Fetch a single service entry (full structure)
print("=" * 60)
print("1. Full service structure (api.aiapi.ch)")
print("=" * 60)
try:
    req = urllib.request.Request("https://api.agentic.market/v1/services/search?q=aiapi",
                                 headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read().decode("utf-8"))
        # Get the api.aiapi.ch service
        services = d.get("services", [])
        for s in services:
            if s.get("id") == "aiapi.ch" or "aiapi" in s.get("name","").lower():
                print(json.dumps(s, indent=2)[:4000])
                break
        else:
            if services:
                print(json.dumps(services[0], indent=2)[:4000])
except Exception as e:
    print(f"err: {e}")

# 2) Look at the full list
print()
print("=" * 60)
print("2. Full services list (first 3 entries)")
print("=" * 60)
try:
    req = urllib.request.Request("https://api.agentic.market/v1/services",
                                 headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read().decode("utf-8"))
        services = d.get("services", [])
        print(f"Total services: {len(services)}")
        for s in services[:3]:
            print(json.dumps(s, indent=2)[:2500])
            print("---")
except Exception as e:
    print(f"err: {e}")

# 3) Look at the agentic.market home page text for submission hints
print()
print("=" * 60)
print("3. agentic.market page — submission hints (raw text)")
print("=" * 60)
try:
    req = urllib.request.Request("https://agentic.market", headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode("utf-8")
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", body)
        text = re.sub(r"\s+", " ", text)
        # Find any submit/add hints
        for kw in ["submit", "add your", "list your", "register", "include", "add to", "how to"]:
            for m in re.finditer(kw, text, re.IGNORECASE):
                start = max(0, m.start()-80)
                end = min(len(text), m.end()+200)
                snippet = text[start:end]
                print(f"  '{kw}': ...{snippet}...")
                break
        # Also print first 1000 chars of text
        print()
        print("First 1000 chars:", text[:1000])
except Exception as e:
    print(f"err: {e}")

# 4) Check docs.cdp.coinbase.com/x402 for submission
print()
print("=" * 60)
print("4. CDP x402 docs — submission process")
print("=" * 60)
try:
    req = urllib.request.Request("https://docs.cdp.coinbase.com/x402/welcome",
                                 headers={"User-Agent":"razel369-aia/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode("utf-8")
        text = re.sub(r"<[^>]+>", " ", body)
        text = re.sub(r"\s+", " ", text)
        for kw in ["submit", "register", "list your", "add to bazaar", "publish"]:
            for m in re.finditer(kw, text, re.IGNORECASE):
                start = max(0, m.start()-80)
                end = min(len(text), m.end()+200)
                print(f"  '{kw}': ...{text[start:end]}...")
                break
        print()
        print("First 1500 chars:", text[:1500])
except Exception as e:
    print(f"err: {e}")
