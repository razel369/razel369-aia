#!/usr/bin/env python3
"""EIP-3009 TransferWithAuthorization signer + x402 payment client.
This will let AIA auto-index in the CDP Bazaar once any wallet has USDC.
Generates a new wallet, but won't auto-fund (no free OAuth-less faucet exists)."""
import json, os, secrets, hashlib
from eth_account import Account
from eth_account.messages import encode_typed_data
import coincurve

# Generate fresh wallet
acct = Account.create()
print(f"NEW WALLET: {acct.address}")
print(f"PRIVATE KEY: {acct.key.hex()}")

# USDC Base contract addresses
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
USDC_NAME = "USD Coin"
USDC_VERSION = "2"

# EIP-712 domain
def domain(network):
    return {
        "name": USDC_NAME,
        "version": USDC_VERSION,
        "chainId": 84532 if "sepolia" in network else 8453,
        "verifyingContract": USDC_BASE_SEPOLIA if "sepolia" in network else USDC_BASE
    }

# EIP-3009 TransferWithAuthorization types
TYPES = {
    "TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"}
    ]
}

def sign_authorization(payer_key, pay_to, value_usdc_units, valid_before_unix, network="base-sepolia"):
    """Sign an EIP-3009 TransferWithAuthorization."""
    nonce = "0x" + secrets.token_hex(32)
    msg = {
        "from": Account.from_key(payer_key).address,
        "to": pay_to,
        "value": str(value_usdc_units),
        "validAfter": 0,
        "validBefore": valid_before_unix,
        "nonce": nonce
    }
    typed = encode_typed_data(domain(network), TYPES, msg)
    sig = Account.sign_message(typed, payer_key)
    return {
        "from": msg["from"],
        "to": msg["to"],
        "value": msg["value"],
        "validAfter": msg["validAfter"],
        "validBefore": msg["validBefore"],
        "nonce": msg["nonce"],
        "v": int(sig.v),
        "r": hex(sig.r),
        "s": hex(sig.s)
    }

# Example: sign $0.01 (10000 microUSDC) authorization
# payer = acct (the new wallet)
# pay_to = AIA operator
import time
auth = sign_authorization(
    acct.key,
    "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    10000,
    int(time.time()) + 300,
    "base-sepolia"
)
print()
print("SAMPLE AUTHORIZATION (signed):")
print(json.dumps(auth, indent=2))

# The x402 payment payload is:
# {
#   "x402Version": 2,
#   "scheme": "exact",
#   "network": "base-sepolia",
#   "payload": {
#     "signature": auth,
#     "authorization": auth
#   }
# }
print()
print("To use this, the wallet must hold testnet USDC on Base Sepolia.")
print("No free public faucet exists that doesn't require OAuth login.")
