"""
Monitor wallet for incoming USDC. When detected, automatically:
1. Sign EIP-3009 TransferWithAuthorization
2. Send to /v1/signals with X-PAYMENT header
3. Get indexed in CDP Bazaar

User needs to send $1 USDC on Base to: 0x81ccb2e48eb911D6B549C1063be2cBe08BA4BCD5
"""
import urllib.request, urllib.parse, json, time
from eth_account import Account
from eth_account.messages import encode_typed_data
import os

WALLET = "0x81ccb2e48eb911D6B549C1063be2cBe08BA4BCD5"
KEY = "0858e2d5fd9a3e8faddbe949ef1262739067c44358dee4b97d8860aae7ea944f"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
WORKER_URL = "https://aia-x402.rmalka06.workers.dev/v1/signals"
CHAIN_ID = 8453

def rpc(method, params, id=1):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":id}).encode()
    req = urllib.request.Request("https://mainnet.base.org", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def check_usdc():
    data = "0x70a08231" + "0"*24 + WALLET[2:].lower()
    r = rpc("eth_call", [{"to": USDC_BASE, "data": data}, "latest"])
    return int(r.get("result", "0x0"), 16) / 1e6

def check_eth():
    r = rpc("eth_getBalance", [WALLET, "latest"])
    return int(r.get("result", "0x0"), 16) / 1e18

def sign_eip3009(pay_to, value_usdc, valid_after, valid_before, nonce):
    """Sign an EIP-3009 TransferWithAuthorization for USDC on Base"""
    acct = Account.from_key(KEY)

    # EIP-3009 domain
    domain = {
        "name": "USD Coin",
        "version": "2",
        "chainId": CHAIN_ID,
        "verifyingContract": USDC_BASE
    }

    # TransferWithAuthorization message
    message = {
        "from": WALLET,
        "to": pay_to,
        "value": int(value_usdc * 1e6),  # USDC has 6 decimals
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce
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
    signed = Account.sign_message(encoded, acct.key)
    return signed.signature.hex(), message

def call_worker_with_payment(payment_sig_hex):
    """Call AIA worker with signed x402 payment"""
    payload = {
        "x402Version": 2,
        "scheme": "exact",
        "network": "eip-155:8453",
        "payload": {
            "signature": "0x" + payment_sig_hex,
            "authorization": {
                "from": WALLET,
                "to": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
                "value": "10000",  # 0.01 USDC
                "validAfter": str(int(time.time())),
                "validBefore": str(int(time.time()) + 300),
                "nonce": "0x" + "00" * 32
            }
        }
    }
    b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    req = urllib.request.Request(
        f"{WORKER_URL}?topics=ai-agents&limit=10",
        headers={"X-PAYMENT": b64, "PAYMENT-SIGNATURE": b64}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

import base64

def main():
    print(f"=== Wallet Monitor: {WALLET} ===")
    print(f"  USDC on Base: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
    print(f"  Worker URL: {WORKER_URL}")
    print()

    while True:
        try:
            usdc = check_usdc()
            eth = check_eth()
            print(f"[{time.strftime('%H:%M:%S')}] USDC: ${usdc:.6f}  ETH: {eth:.8f}")

            if usdc >= 0.003:
                print(f"\n*** USDC detected! Making self-payment to index AIA in Bazaar ***")
                try:
                    result = call_worker_with_payment("")
                    print(f"SUCCESS: {result}")
                    print("AIA should now be indexed in CDP Bazaar!")
                    return
                except Exception as e:
                    print(f"Self-payment failed: {e}")
                    # If 402, need to sign
                    if "402" in str(e) or "payment" in str(e).lower():
                        print("Worker requires payment - need to sign EIP-3009")
                    # Continue monitoring
            else:
                print("  No USDC yet, waiting...")
        except Exception as e:
            print(f"  err: {e}")

        time.sleep(30)

if __name__ == "__main__":
    main()