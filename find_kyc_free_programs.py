#!/usr/bin/env python3
"""Get specific KYC/payout details from Immunefi programs."""
import os, json, urllib.request, ssl, urllib.error, re

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")
ctx = ssl.create_default_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/plain",
}

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode()
    except Exception as e:
        return f"ERR: {e}"

# Programs to evaluate
programs = [
    ("thegraph", "The Graph", "$50K"),
    ("lombard-finance", "Lombard Finance", "$250K"),
    ("ssvnetwork", "SSV Network", "$250K"),
    ("ens", "ENS", "$250K"),
    ("dexeprotocol", "DeXe Protocol", "$500K"),
    ("hedera", "Hedera", "$30K"),
    ("starknet", "Starknet", "$?K"),
    ("polygon", "Polygon", "$?K"),
    ("arbitrum", "Arbitrum", "$?K"),
    ("optimism", "Optimism", "$?K"),
    ("wormhole", "Wormhole", "$10M (largest)"),
    ("celestia", "Celestia", "$?K"),
    ("sui", "Sui", "$?K"),
    ("aptos", "Aptos", "$?K"),
    ("morpho", "Morpho", "$?K"),
    ("aave", "Aave", "$?K"),
    ("uniswap", "Uniswap", "$?K"),
    ("compound", "Compound", "$?K"),
    ("maker", "MakerDAO", "$?K"),
    ("curve", "Curve", "$?K"),
    ("convex", "Convex", "$?K"),
    ("yearn", "Yearn", "$?K"),
    ("frax", "Frax", "$?K"),
    ("rocketpool", "Rocket Pool", "$?K"),
    ("lido", "Lido", "$?K"),
    ("chainlink", "Chainlink", "$?K"),
    ("dydx", "dYdX", "$?K"),
    ("gmx", "GMX", "$?K"),
    ("synthetix", "Synthetix", "$?K"),
    ("balancer", "Balancer", "$?K"),
]

print("=" * 70)
print("IMMUNEFI PROGRAM ANALYSIS - KYC + Payout")
print("=" * 70)

results = []

for slug, name, max_b in programs:
    text = fetch(f"https://r.jina.ai/https://immunefi.com/bug-bounty/{slug}/information")
    if "ERR" in text[:10]:
        results.append({"name": name, "max": max_b, "kyc": "?", "payout": "?", "poc": "?", "safe_harbor": "N", "total_paid": "?"})
        continue

    # KYC check
    kyc_required = "KYC required" in text or "KYC Required" in text
    kyc_free = "KYC Not Required" in text or "KYC not required" in text

    # PoC
    poc_required = "PoC Required" in text or "PoC required" in text

    # Payout
    payout = "?"
    if "Rewards are distributed" in text:
        idx = text.find("Rewards are distributed")
        chunk = text[idx:idx+500]
        if "USDC" in chunk: payout = "USDC"
        elif "ETH" in chunk: payout = "ETH"
        elif "USDT" in chunk: payout = "USDT"

    # Safe Harbor
    safe_harbor = "Safe Harbor" in text

    # Find max bounty
    m = re.search(r'Maximum Bounty.*?\$([\d,]+)', text, re.DOTALL)
    actual_max = m.group(1) if m else "?"

    # Total paid
    m2 = re.search(r'Total Paid.*?\$([\d.KM]+)', text, re.DOTALL)
    total_paid = m2.group(1) if m2 else "?"

    results.append({
        "name": name, "max": actual_max, "kyc": "YES" if kyc_required else ("NO" if kyc_free else "?"),
        "poc": "YES" if poc_required else "?",
        "payout": payout, "safe_harbor": "Y" if safe_harbor else "N",
        "total_paid": total_paid
    })

# Print
print(f"{'Name':<25} {'Max':<10} {'KYC':<5} {'PoC':<5} {'Payout':<8} {'Safe Harbor':<12} {'Paid'}")
print("-" * 90)
for r in results:
    print(f"{r['name']:<25} ${r['max']:<9} {r['kyc']:<5} {r['poc']:<5} {r['payout']:<8} {r.get('safe_harbor','?'):<12} {r.get('total_paid','?')}")

# Find the BEST targets: NO KYC + high max
print()
print("=" * 70)
print("BEST TARGETS — KYC NOT REQUIRED + HIGH MAX BOUNTY")
print("=" * 70)
kyc_free = [r for r in results if r["kyc"] == "NO"]
kyc_free.sort(key=lambda x: float(x["max"].replace(",", "").replace("K", "000").replace("M", "000000")) if x["max"] not in ("?", "") else 0, reverse=True)
for r in kyc_free:
    print(f"  {r['name']}: ${r['max']}, PoC={r['poc']}, payout={r['payout']}, paid={r.get('total_paid','?')}")
