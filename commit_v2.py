#!/usr/bin/env python3
"""Commit + push all the new work to GitHub."""
import subprocess, os, json

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

# Add everything
r = subprocess.run(["git","add","-A"], capture_output=True, text=True, timeout=30)
print(f"add: {r.returncode} | {r.stderr[:200]}")

# Status check
r = subprocess.run(["git","status","--short"], capture_output=True, text=True, timeout=10)
lines = r.stdout.strip().split("\n")
print(f"uncommitted: {len(lines)} files")
for l in lines[:20]:
    print(f"  {l}")

# Commit
msg = """v2: AIA worker uses CDP facilitator + CDP-compliant Bazaar extension

- Switched primary facilitator to https://api.cdp.coinbase.com/platform/v2/x402
  so any successful payment auto-indexes AIA in the Coinbase CDP Bazaar
  (and downstream x402scan / Agentic.Market / Merit-Systems sync)
- Reworked bazaar extension to match CDP's expected schema exactly:
  - extensions.bazaar.discoverable
  - extensions.bazaar.category
  - extensions.bazaar.tags
  - extensions.bazaar.info (with input/output examples)
  - extensions.bazaar.schema (full JSON schema)
  - accepts[0].outputSchema (input/output in the accept body)
- Testnet support: ?testnet=1 switches to base-sepolia
- EIP-3009 TransferWithAuthorization signer (eip3009_signer.py) ready
- New wallet generator integrated
- CDP facilitator needs auth (CDP API key required) — fallback to x402.org/facilitator
  if env.ALLOW_FALLBACK=1
- Health endpoint now exposes cdp_facilitator + fallback_facilitator + per-route bazaar tags
"""
r = subprocess.run(["git","commit","-m",msg], capture_output=True, text=True, timeout=30)
print(f"\ncommit: {r.returncode}")
print(f"  out: {r.stdout[:300]}")
if r.stderr: print(f"  err: {r.stderr[:300]}")

# Push
r = subprocess.run(["git","push","origin","main"], capture_output=True, text=True, timeout=120)
print(f"\npush: {r.returncode}")
print(f"  out: {r.stdout[:300]}")
print(f"  err: {r.stderr[:300]}")

# Verify
r = subprocess.run(["git","log","--oneline","-5"], capture_output=True, text=True, timeout=10)
print(f"\nlast 5 commits:\n{r.stdout}")
