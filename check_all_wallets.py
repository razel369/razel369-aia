"""Check all wallet balances across chains after user deposit."""
import urllib.request, json

addresses = {
    "operator": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "D32A": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
    "0x86f3": "0x86f3666720d54c531c723201BA49403D7c42c564",
    "0xb108": "0xb10871882b12051b5531dBcaf0a564082aB41CeF",
}

CHAINS = {
    "Base": "https://mainnet.base.org",
    "Arbitrum": "https://arb1.arbitrum.io/rpc",
    "Optimism": "https://mainnet.optimism.io",
    "Ethereum": "https://eth.llamarpc.com",
}

USDC = {
    "Base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "Arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "Optimism": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
    "Ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
}

def rpc(url, method, params, id=1):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":id}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def to_int(hexstr):
    if not hexstr or hexstr == '0x': return 0
    return int(hexstr, 16)

# Print header
print(f"{'Wallet':<10} {'Chain':<10} {'ETH':<15} {'USDC':<10}")
print("-" * 50)

for name, addr in addresses.items():
    for chain_name, rpc_url in CHAINS.items():
        try:
            # ETH balance
            r = rpc(rpc_url, "eth_getBalance", [addr, "latest"])
            eth_wei = to_int(r.get("result", "0x0"))
            eth = eth_wei / 1e18

            # USDC balance
            usdc_addr = USDC[chain_name]
            data = "0x70a08231" + "0"*24 + addr[2:].lower()
            r2 = rpc(rpc_url, "eth_call", [{"to": usdc_addr, "data": data}, "latest"])
            usdc_raw = to_int(r2.get("result", "0x0"))
            usdc = usdc_raw / 1e6

            if eth > 0 or usdc > 0:
                print(f"{name:<10} {chain_name:<10} {eth:<15.6f} ${usdc:<10.2f}")
        except Exception as e:
            pass

print()
print("=== Transaction history check via BaseScan ===")
for name, addr in addresses.items():
    try:
        url = f"https://api.basescan.org/api?module=account&action=txlist&address={addr}&page=1&offset=5&sort=desc"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
            txs = data.get("result", [])
            if txs and isinstance(txs, list) and len(txs) > 0:
                print(f"\n{name} ({addr}): {len(txs)} recent txs")
                for tx in txs[:3]:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(int(tx.get("timeStamp","0")))
                    val_eth = int(tx.get("value","0")) / 1e18
                    print(f"  {dt}  {val_eth} ETH  from {tx.get('from')[:10]}... to {tx.get('to')[:10]}...")
            else:
                print(f"{name}: 0 txs on Base")
    except Exception as e:
        print(f"{name} err: {e}")
