"""SELF-PAYMENT TO INDEX AIA IN CDP BAZAAR using requests library."""
import json, time, base64, secrets
import requests
from eth_account import Account
from eth_account.messages import encode_typed_data

WALLET = "0x81ccb2e48eb911D6B549C1063be2cBe08BA4BCD5"
KEY = "0858e2d5fd9a3e8faddbe949ef1262739067c44358dee4b97d8860aae7ea944f"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
RECIPIENT = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"
WORKER_URL = "https://aia-x402.rmalka06.workers.dev/v1/signals"
CHAIN_ID = 8453
PRICE_USDC = 0.01

def rpc(method, params, id=1):
    """Use public RPC with proper headers."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":id})
    r = requests.post("https://mainnet.base.org", data=body, headers=headers, timeout=20)
    return r.json()

def check_usdc():
    data = "0x70a08231" + "0"*24 + WALLET[2:].lower()
    r = rpc("eth_call", [{"to": USDC_BASE, "data": data}, "latest"])
    return int(r.get("result", "0x0"), 16) / 1e6

def check_nonce():
    r = rpc("eth_getTransactionCount", [WALLET, "pending"])
    return int(r.get("result", "0x0"), 16)

def main():
    print("=" * 60)
    print("SELF-PAYMENT TO INDEX AIA IN CDP BAZAAR")
    print("=" * 60)

    usdc = check_usdc()
    print(f"\nUSDC balance: ${usdc:.6f}")
    print(f"Wallet: {WALLET}")
    print(f"Recipient (AIA operator): {RECIPIENT}")
    print(f"Network: Base (chainId {CHAIN_ID})")
    print(f"Asset: USDC ({USDC_BASE})")

    if usdc < PRICE_USDC:
        print(f"INSUFFICIENT: need ${PRICE_USDC}, have ${usdc:.6f}")
        return

    print(f"\n[1/3] Signing EIP-3009 TransferWithAuthorization...")
    valid_after = int(time.time()) - 60
    valid_before = int(time.time()) + 600
    nonce_bytes = "0x" + secrets.token_hex(32)

    domain = {
        "name": "USD Coin",
        "version": "2",
        "chainId": CHAIN_ID,
        "verifyingContract": USDC_BASE
    }
    message = {
        "from": WALLET,
        "to": RECIPIENT,
        "value": int(PRICE_USDC * 1e6),
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce_bytes
    }
    types = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"}
        ],
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"}
        ]
    }

    encoded = encode_typed_data(domain, types, message)
    signed = Account.sign_message(encoded, KEY)
    sig = "0x" + signed.signature.hex()
    print(f"  Signed: {sig[:30]}...{sig[-10:]}")
    print(f"  Value: {int(PRICE_USDC * 1e6)} (= {PRICE_USDC} USDC)")

    payload = {
        "x402Version": 2,
        "scheme": "exact",
        "network": "eip-155:8453",
        "payload": {
            "signature": sig,
            "authorization": {
                "from": WALLET,
                "to": RECIPIENT,
                "value": str(int(PRICE_USDC * 1e6)),
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": nonce_bytes
            }
        }
    }
    b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    print(f"\n[2/3] Base64 payload ready ({len(b64)} chars)")

    print(f"\n[3/3] Calling worker: {WORKER_URL}")
    print("=" * 60)

    url = f"{WORKER_URL}?topics=ai-agents,crypto&limit=5"
    headers = {
        "X-PAYMENT": b64,
        "PAYMENT-SIGNATURE": b64,
        "User-Agent": "AIA-self-payment/1.0",
        "Accept": "application/json"
    }

    try:
        r = requests.get(url, headers=headers, timeout=60)
        print(f"\nSTATUS: {r.status_code}")
        print(f"\nRESPONSE:")
        try:
            data = r.json()
            print(json.dumps(data, indent=2)[:3000])
        except:
            print(r.text[:2000])
        return r.status_code, r.text
    except Exception as e:
        print(f"ERROR: {e}")
        return None, str(e)

if __name__ == "__main__":
    status, body = main()
    if status == 200:
        print("\n" + "=" * 60)
        print("SUCCESS - AIA WORKER PAID!")
        print("AIA should now be auto-indexed in CDP Bazaar!")
        print("=" * 60)
    else:
        print(f"\nFailed with status {status}")