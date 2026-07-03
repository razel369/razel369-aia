#!/usr/bin/env python3
"""AGGRESSIVE bounty research: illbnm + Algora + every high-value USDC source."""
import json, urllib.request, urllib.error, urllib.parse, re, base64, time

def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"User-Agent":"razel369-aia/1.0","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]

def fetch(url, headers=None, method="GET", data=None, timeout=30):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            try: return r.status, json.loads(text)
            except: return r.status, text
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return -1, str(e)

# 1) illbnm/homelab-stack issues
print("=" * 60)
print("illbnm/homelab-stack issues")
print("=" * 60)
s, d = gh("/repos/illbnm/homelab-stack/issues?state=open&per_page=30")
if s == 200:
    for it in d:
        if "pull_request" in it: continue
        labels = [l.get("name") for l in it.get("labels",[])]
        print(f"  #{it.get('number')} [{','.join(labels[:3])}] {it.get('title')[:80]}")
        print(f"    body: {(it.get('body','') or '')[:400]}")

# 2) Algora direct API for top orgs
print()
print("=" * 60)
print("Algora API for many orgs")
print("=" * 60)
algora_orgs = [
    "algora-io", "tursodatabase", "dwebagents", "permitio",
    "golemcloud", "biomejs", "turbo-oss", "ubounty-app",
    "astral-sh", "denoland", "vercel", "withastro",
    "virtuals-protocol", "all-hands-ai", "modal-labs",
    "router-protocol", "polygon", "starknet-io", "aptos-labs",
    "sui-foundation", "solana-labs", "celestiaorg",
    "injective", "osmosis-labs", "cosmos", "ethereum",
    "matter-labs", "starkware", "optimism", "arbitrum",
    "scroll-tech", "linea", "base", "zksync",
    "manta-network", "blast-io", "mode-network", "worldcoin",
    "Galxe", "Layer3xyz", "rabbit-hole", "paragraph-protocol",
    "phala-network", "litentry", "oceanprotocol", "fetch-ai",
    "SingularityNET", "numerai", "cohere", "mistralai",
    "ollama", "open-webui", "lmstudio", "ggerganov",
    "huggingface", "unslothai", "axolotl-ai-cloud", "oobabooga",
    "janhq", "koboldai", "Stability-AI", "comfyanonymous",
    "kohya-ss", "lllyasviel", "invoke-ai", "hardmaru",
    "trustwallet", "metamask", "rainbow-me", "walletconnect",
    "safe-global", "zerion-io", "firefly", "frame",
    "litecoin-project", "bitcoin", "dogecoin", "monero-project",
    "zcash", "cardano-foundation", "algorand", "tezos",
]
print(f"checking {len(algora_orgs)} orgs...")
total_found = 0
for org in algora_orgs:
    s, d = fetch(f"https://api.algora.io/api/orgs/{org}/bounties?status=open", timeout=10)
    if s == 200 and isinstance(d, list) and len(d) > 0:
        for b in d:
            amt = b.get("usdValue") or b.get("usd_value") or 0
            print(f"  {org} #{b.get('id')}: ${amt} {b.get('title','')[:60]}")
            total_found += 1
print(f"\nTotal Algora bounties found: {total_found}")

# 3) GitHub issues with "bounty" + actual money
print()
print("=" * 60)
print("GitHub: issues with bounty tag AND USDC amount")
print("=" * 60)
queries = [
    '"$50" label:bounty is:issue is:open',
    '"$100" label:bounty is:issue is:open',
    '"$200" label:bounty is:issue is:open',
    '"$300" label:bounty is:issue is:open',
    '"$500" label:bounty is:issue is:open',
    '"$1000" label:bounty is:issue is:open',
    'USDC label:bounty is:issue is:open',
    'Algora is:issue is:open',
    'is:open author:gryphonmyers',  # the guy who set up our 23 USDC bounty
]
for q in queries:
    s, d = gh(f"/search/issues?q={urllib.parse.quote(q)}&per_page=10")
    if s == 200:
        items = d.get("items", [])
        if items:
            print(f"  q={q!r}: {len(items)} issues")
            for it in items[:5]:
                print(f"    #{it.get('number')} {it.get('repository_url','').split('/')[-1]} ${it.get('title')[:60]}")

# 4) Find more bounty platforms
print()
print("=" * 60)
print("Other bounty platforms via search")
print("=" * 60)
queries2 = [
    "AI agent bounty marketplace",
    "GitHub bounty USDC Base",
    "Algora bounty list",
    "agentic marketplace paid API",
    "x402 bounty",
    "x402 paid service marketplace",
]
for q in queries2:
    s, d = gh(f"/search/repositories?q={urllib.parse.quote(q)}&per_page=5")
    if s == 200:
        for it in d.get("items",[])[:3]:
            print(f"  ★{it.get('stargazers_count',0):>4}  {it.get('full_name')}: {it.get('description','')[:80]}")
