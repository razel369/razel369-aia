"""Check operator wallet on BSC for ALL BEP-20 tokens and tx history."""
import urllib.request, json
from datetime import datetime

operator = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

# BscScan API
BSC_API = "https://api.bscscan.com/api"

# 1. Check BNB balance via BSC node
def rpc(url, method, params, id=1):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":id}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def to_int(hexstr):
    if not hexstr or hexstr == '0x': return 0
    return int(hexstr, 16)

# BNB
r = rpc("https://bsc-dataseed.binance.org", "eth_getBalance", [operator, "latest"])
bnb = to_int(r.get("result", "0x0")) / 1e18
print(f"Operator BNB: {bnb}")

# 2. Check tx list on BscScan
print("\n=== BscScan transactions ===")
url = f"{BSC_API}?module=account&action=txlist&address={operator}&page=1&offset=20&sort=desc"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode())
    txs = data.get("result", [])
    if isinstance(txs, list):
        print(f"Found {len(txs)} txs on BSC")
        for tx in txs[:15]:
            dt = datetime.fromtimestamp(int(tx.get("timeStamp","0")))
            val = int(tx.get("value","0")) / 1e18
            is_in = tx.get("to","").lower() == operator.lower()
            direction = "IN " if is_in else "OUT"
            print(f"  {dt}  {direction}  {val:.6f} BNB  from {tx.get('from','')[:14]}... to {tx.get('to','')[:14]}...")
            print(f"    hash: {tx.get('hash','')}")
except Exception as e:
    print(f"BscScan err: {e}")

# 3. Check BEP-20 token transfers
print("\n=== BEP-20 token transfers ===")
url = f"{BSC_API}?module=account&action=tokentx&address={operator}&page=1&offset=20&sort=desc"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode())
    txs = data.get("result", [])
    if isinstance(txs, list):
        print(f"Found {len(txs)} BEP-20 txs")
        for tx in txs[:15]:
            dt = datetime.fromtimestamp(int(tx.get("timeStamp","0")))
            decimals = int(tx.get("tokenDecimal","18"))
            val = int(tx.get("value","0")) / (10**decimals)
            sym = tx.get("tokenSymbol","?")
            name = tx.get("tokenName","?")
            is_in = tx.get("to","").lower() == operator.lower()
            direction = "IN " if is_in else "OUT"
            print(f"  {dt}  {direction}  {val:,.4f} {sym}  ({name})")
            print(f"    contract: {tx.get('contractAddress','')}")
            print(f"    hash: {tx.get('hash','')}")
except Exception as e:
    print(f"BscScan err: {e}")

# 4. Get current token balances via BscScan (free)
print("\n=== Current BEP-20 balances ===")
url = f"{BSC_API}?module=account&action=tokenbalance&address={operator}&tag=latest"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode())
    print(json.dumps(data, indent=2)[:1500])
except Exception as e:
    print(f"err: {e}")

# 5. Check USDT/USDC on BSC
print("\n=== Check USDC on BSC directly ===")
USDC_BSC = "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
USDT_BSC = "0x55d398326f99059fF775485246999027B3197955"
for name, addr in [("USDC", USDC_BSC), ("USDT", USDT_BSC), ("DAI", "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3")]:
    data = "0x70a08231" + "0"*24 + operator[2:].lower()
    r2 = rpc("https://bsc-dataseed.binance.org", "eth_call", [{"to": addr, "data": data}, "latest"])
    bal = to_int(r2.get("result", "0x0"))
    if bal > 0:
        print(f"  {name}: {bal/1e18}")
