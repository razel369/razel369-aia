"""Check ALL my wallets on ALL chains including BNB Chain, Fantom, etc."""
import urllib.request, json
from datetime import datetime

# All addresses I might have given the user
addresses = {
    "operator (Binance deposit)": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "D32A (recommended)": "0xD32A3a5E29eeb37f2A95a8617013438afffA00E2",
    "0x86f3 (from key 0xb833)": "0x86f3666720d54c531c723201BA49403D7c42c564",
    "0xb108 (test wallet)": "0xb10871882b12051b5531dBcaf0a564082aB41CeF",
}

# Many chains
CHAINS = {
    "Ethereum": "https://eth.llamarpc.com",
    "Base": "https://mainnet.base.org",
    "Arbitrum": "https://arb1.arbitrum.io/rpc",
    "Optimism": "https://mainnet.optimism.io",
    "Polygon": "https://polygon-rpc.com",
    "BSC": "https://bsc-dataseed.binance.org",
    "Avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "Fantom": "https://rpc.ftm.tools",
    "Gnosis": "https://rpc.gnosischain.com",
    "zkSync": "https://mainnet.era.zksync.io",
    "Linea": "https://rpc.linea.build",
    "Scroll": "https://rpc.scroll.io",
    "Mantle": "https://rpc.mantle.xyz",
    "Manta": "https://pacific-rpc.manta.network/http",
    "Blast": "https://rpc.blast.io",
    "Mode": "https://mainnet.mode.network",
    "Zora": "https://rpc.zora.energy",
    "World": "https://worldchain-mainnet.g.alchemy.com/public",
    "Sei": "https://evm-rpc.sei.io",
    "Celo": "https://forno.celo.org",
    "Aurora": "https://mainnet.aurora.dev",
    "Kava": "https://evm.kava.io",
    "Metis": "https://andromeda.metis.io/?owner=1088",
    "Klaytn": "https://public-en-cypress.klaytnbase.com",
    "Cronos": "https://evm.cronos.org",
    "Moonbeam": "https://rpc.api.moonbeam.network",
    "Injective": "https://sentry.evm-rpc.injective.network",
    "opBNB": "https://opbnb-mainnet-rpc.bnbchain.org",
    "Base Sepolia": "https://sepolia.base.org",
    "Arbitrum Sepolia": "https://sepolia-rollup.arbitrum.io/rpc",
    "Optimism Sepolia": "https://sepolia.optimism.io",
    "Ethereum Sepolia": "https://ethereum-sepolia-rpc.publicnode.com",
    "Polygon Amoy": "https://rpc-amoy.polygon.technology",
}

USDC = {
    "Ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "Base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "Arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "Optimism": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
    "Polygon": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    "BSC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
    "Avalanche": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
    "Fantom": "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75",
    "Gnosis": "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",
    "zkSync": "0x1d17CBcF0D6D143135aE902365D84E5F3039f007",
    "Linea": "0x176211869cA2b568f2A7D4EE941E0732f27B9E75",
    "Scroll": "0x06eFdBFf2a14a7c8E15944D620F7Ee3FE55adD38",
    "Mantle": "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9",
    "Manta": "0xb73603C5d87f094AbB23c7FDe45f6a11DB7F2F03",
    "Blast": "0x4300000000000000000000000000000000000003",
}

def rpc(url, method, params, id=1):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":id}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode())

def to_int(hexstr):
    if not hexstr or hexstr == '0x': return 0
    return int(hexstr, 16)

# Check ALL
print(f"{'Wallet':<32} {'Chain':<18} {'Native':<14} {'USDC':<10}")
print("-" * 80)

found_any = False
for name, addr in addresses.items():
    for chain_name, rpc_url in CHAINS.items():
        try:
            r = rpc(rpc_url, "eth_getBalance", [addr, "latest"])
            wei = to_int(r.get("result", "0x0"))
            if wei > 0:
                native = wei / 1e18
                print(f"  {name:<30} {chain_name:<18} {native:<14.8f}")
                found_any = True

            if chain_name in USDC:
                data = "0x70a08231" + "0"*24 + addr[2:].lower()
                r2 = rpc(rpc_url, "eth_call", [{"to": USDC[chain_name], "data": data}, "latest"])
                bal = to_int(r2.get("result", "0x0"))
                if bal > 0:
                    usdc = bal / 1e6
                    print(f"  {name:<30} {chain_name:<18} {usdc:<14.6f} USDC")
                    found_any = True
        except: pass

if not found_any:
    print("  NO BALANCES FOUND ON ANY CHAIN")
print()

# Now check txs via explorers for ALL chains
print("=== Transaction history on all chains (last 30 days) ===\n")
EXPLORERS = {
    "Ethereum": "https://api.etherscan.io/api?chainid=1",
    "Base": "https://api.etherscan.io/api?chainid=8453",
    "Arbitrum": "https://api.etherscan.io/api?chainid=42161",
    "Optimism": "https://api.etherscan.io/api?chainid=10",
    "Polygon": "https://api.etherscan.io/api?chainid=137",
    "BSC": "https://api.etherscan.io/api?chainid=56",
    "Avalanche": "https://api.etherscan.io/api?chainid=43114",
    "Fantom": "https://api.ftmscan.com/api",
    "Gnosis": "https://api.gnosisscan.io/api",
}

for name, addr in addresses.items():
    found_tx = False
    for chain_name, api_url in EXPLORERS.items():
        try:
            url = f"{api_url}&module=account&action=txlist&address={addr}&page=1&offset=3&sort=desc"
            with urllib.request.urlopen(url, timeout=8) as r:
                data = json.loads(r.read().decode())
            txs = data.get("result", [])
            if isinstance(txs, list) and txs:
                if not found_tx:
                    print(f"  {name} ({addr}):")
                    found_tx = True
                for tx in txs[:2]:
                    dt = datetime.fromtimestamp(int(tx.get("timeStamp","0")))
                    val = int(tx.get("value","0")) / 1e18
                    print(f"    [{chain_name}] {dt}  {val} native  hash={tx.get('hash','')[:20]}...")
        except: pass
    if not found_tx:
        print(f"  {name}: 0 txs on all chains")
