#!/usr/bin/env python3
"""Audit L1GraphTokenGateway - look for cross-chain bridge vulnerabilities."""
import os, re, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\audit_graph\contracts")
ctx = ssl.create_default_context()

# Read the L1 gateway
with open("packages/contracts/contracts/gateway/L1GraphTokenGateway.sol") as f:
    L1 = f.read()

# Find all function signatures
print("=" * 70)
print("L1GraphTokenGateway - FUNCTIONS")
print("=" * 70)
funcs = re.findall(r"function\s+(\w+)\s*\(([^)]*)\)\s+([^{]+)\s*\{", L1)
for name, args, mods in funcs:
    print(f"  {name}({args.strip()}) {mods.strip()}")

# Find minting-related code
print()
print("=" * 70)
print("L1GraphTokenGateway - MINT-related code")
print("=" * 70)
for line in L1.split('\n'):
    if any(kw in line.lower() for kw in ["mint", "l2mint", "finalize", "setl2", "allowance", "callhook"]):
        s = line.strip()
        if s and not s.startswith("//"):
            print(f"  {s[:200]}")

# Look for the critical function: setL2MintAllowance
print()
print("=" * 70)
print("L1GraphTokenGateway - setL2MintAllowance function (if exists)")
print("=" * 70)
m = re.search(r"function\s+setL2MintAllowance\s*\([^)]*\)\s+(?:external|public|internal|private)[^{]+\{(.*?)\n\s*\}", L1, re.DOTALL)
if m:
    print(m.group(0))

# Check GraphTokenGateway (parent class)
print()
print("=" * 70)
print("GraphTokenGateway - parent class")
print("=" * 70)
with open("packages/contracts/contracts/gateway/GraphTokenGateway.sol") as f:
    G = f.read()
print(f"  {len(G.split(chr(10)))} lines")
funcs = re.findall(r"function\s+(\w+)\s*\(([^)]*)\)\s+([^{]+)\s*\{", G)
for name, args, mods in funcs:
    print(f"  {name}({args.strip()}) {mods.strip()}")

# Finalize inbound
print()
print("=" * 70)
print("GraphTokenGateway - finalizeInboundTransfer")
print("=" * 70)
m = re.search(r"function\s+_finalizeInboundTransfer\s*\([^)]*\)\s+(?:external|public|internal|private|virtual|override)[^{]+\{(.*?)(?=\n\s*(?:function|contract|event)\s|\Z)", G, re.DOTALL)
if m:
    print(m.group(0)[:3000])

# Look at modifier and access control
print()
print("=" * 70)
print("L1GraphTokenGateway - ACCESS CONTROL")
print("=" * 70)
for line in L1.split('\n'):
    if any(kw in line for kw in ["onlyController", "onlyGovernor", "onlyAdmin", "require(msg.sender"]):
        s = line.strip()
        if s:
            print(f"  {s[:200]}")
