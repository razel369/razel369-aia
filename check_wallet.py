import json, urllib.request, time
from datetime import datetime

wallet = "0x81ccb2e48eb911D6B549C1063be2cBe08BA4BCD5"

print("=== All transactions for the wallet ===")
url = f"https://api.basescan.org/api?module=account&action=txlist&address={wallet}&page=1&offset=20&sort=desc"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    if data.get("status") == "1":
        print(f"Found {len(data['result'])} normal txs:")
        for tx in data["result"]:
            t = datetime.fromtimestamp(int(tx["timeStamp"]))
            val = int(tx["value"]) / 1e18
            is_in = tx["to"].lower() == wallet.lower()
            print(f"  {tx['hash'][:18]}... {t} {val} ETH {'IN ' if is_in else 'OUT'} {tx['from'][:12]}... -> {tx['to'][:12]}...")
    else:
        print(f"Error: {data.get('message')}")
except Exception as e:
    print(f"err: {e}")

print()
print("=== All ERC20 token transfers ===")
url = f"https://api.basescan.org/api?module=account&action=tokentx&address={wallet}&page=1&offset=20&sort=desc"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    if data.get("status") == "1":
        print(f"Found {len(data['result'])} token txs:")
        for tx in data["result"]:
            t = datetime.fromtimestamp(int(tx["timeStamp"]))
            decimals = int(tx["tokenDecimal"])
            val = int(tx["value"]) / (10**decimals)
            sym = tx["tokenSymbol"]
            is_in = tx["to"].lower() == wallet.lower()
            print(f"  {sym} {t} {val} {'IN ' if is_in else 'OUT'} {tx['from'][:12]}... -> {tx['to'][:12]}...")
            print(f"    contract: {tx['contractAddress']}")
            print(f"    hash: {tx['hash']}")
    else:
        print(f"Error: {data.get('message')}")
except Exception as e:
    print(f"err: {e}")