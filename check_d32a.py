"""Check D32A wallet on ALL chains for incoming transactions."""
import urllib.request, json
from datetime import datetime

D32A = "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2"

CHAINS = {
    "Ethereum": "https://eth.llamarpc.com",
    "Base": "https://mainnet.base.org",
    "Base Sepolia": "https://sepolia.base.org",
    "Arbitrum": "https://arb1.arbitrum.io/rpc",
    "Arbitrum Sepolia": "https://sepolia-rollup.arbitrum.io/rpc",
    "Optimism": "https://mainnet.optimism.io",
    "OP Sepolia": "https://sepolia.optimism.io",
    "Polygon": "https://polygon-rpc.com",
    "BSC": "https://bsc-dataseed.binance.org",
    "Avalanche": "https://api.avax.network/ext/bc/C/rpc",
}

# Common stablecoin addresses per chain
STABLECOINS = {
    "Ethereum": {"USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F"},
    "Base": {"USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2", "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"},
    "Arbitrum": {"USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"},
    "Optimism": {"USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "USDT": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"},
    "Polygon": {"USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"},
    "BSC": {"USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", "USDT": "0x55d398326f99059fF775485246999027B3197955"},
    "Avalanche": {"USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", "USDT": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7"},
}

EXPLORERS = {
    "Ethereum": "https://api.etherscan.io/api",
    "Base": "https://api.basescan.org/api",
    "Arbitrum": "https://api.arbiscan.io/api",
    "Optimism": "https://api-optimistic.etherscan.io/api",
    "Polygon": "https://api.polygonscan.com/api",
    "BSC": "https://api.bscscan.com/api",
    "Avalanche": "https://api.snowtrace.io/api",
}

def rpc(url, method, params, id=1):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":id}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

print(f"=== D32A BALANCE CHECK: {D32A} ===\n")

# Native + ERC20 balance check
for chain_name, rpc_url in CHAINS.items():
    try:
        r = rpc(rpc_url, "eth_getBalance", [D32A, "latest"])
        wei = int(r.get("result", "0x0"), 16)
        if wei > 0:
            print(f"  {chain_name}: {wei/1e18} native")

        # Check USDC
        if chain_name in STABLECOINS:
            for sym, addr in STABLECOINS[chain_name].items():
                data = "0x70a08231" + "0"*24 + D32A[2:].lower()
                r2 = rpc(rpc_url, "eth_call", [{"to": addr, "data": data}, "latest"])
                bal = int(r2.get("result", "0x0"), 16)
                if bal > 0:
                    print(f"  {chain_name}: {bal/1e6} {sym}")
    except Exception as e:
        pass

# Transaction history via explorers (need API key for Etherscan, but free tier works for some)
print("\n=== RECENT INCOMING TXs (where money came IN) ===\n")
for chain_name, api_url in EXPLORERS.items():
    try:
        url = f"{api_url}?module=account&action=txlist&address={D32A}&page=1&offset=10&sort=desc"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
            txs = data.get("result", [])
            if isinstance(txs, list) and len(txs) > 0:
                print(f"\n{chain_name}: {len(txs)} txs")
                for tx in txs[:5]:
                    dt = datetime.fromtimestamp(int(tx.get("timeStamp","0")))
                    val_eth = int(tx.get("value","0")) / 1e18
                    is_in = tx.get("to","").lower() == D32A.lower()
                    direction = "IN" if is_in else "OUT"
                    print(f"  {dt}  {direction}  {val_eth:.6f} native  from {tx.get('from','')[:14]}... to {tx.get('to','')[:14]}...")
                    print(f"    hash: {tx.get('hash','')}")
            else:
                pass  # no txs
    except Exception as e:
        pass

# Also check ERC20 token transfers
print("\n=== ERC20 TRANSFERS ===\n")
for chain_name, api_url in EXPLORERS.items():
    try:
        url = f"{api_url}?module=account&action=tokentx&address={D32A}&page=1&offset=10&sort=desc"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
            txs = data.get("result", [])
            if isinstance(txs, list) and len(txs) > 0:
                print(f"\n{chain_name}: {len(txs)} token txs")
                for tx in txs[:5]:
                    dt = datetime.fromtimestamp(int(tx.get("timeStamp","0")))
                    decimals = int(tx.get("tokenDecimal","6"))
                    val = int(tx.get("value","0")) / (10**decimals)
                    is_in = tx.get("to","").lower() == D32A.lower()
                    direction = "IN" if is_in else "OUT"
                    sym = tx.get("tokenSymbol","?")
                    print(f"  {dt}  {direction}  {val} {sym}  ({tx.get('tokenName','')})")
                    print(f"    from {tx.get('from','')[:14]}... to {tx.get('to','')[:14]}...")
                    print(f"    hash: {tx.get('hash','')}")
    except Exception as e:
        pass
