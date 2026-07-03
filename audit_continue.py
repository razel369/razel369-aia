#!/usr/bin/env python3
"""Continue The Graph audit: look for HIGH/CRITICAL bugs in the older 0.7.6 contracts.
Focus on: token accounting, storage collisions, edge cases."""
import os, re, urllib.request, ssl, urllib.error

os.chdir(r"C:\Users\rmalk\projects\audit_graph\contracts")
ctx = ssl.create_default_context()

# Read all .sol files in older contracts package
old_contracts = [
    "packages/contracts/contracts/staking/Staking.sol",
    "packages/contracts/contracts/staking/L1Staking.sol",
    "packages/contracts/contracts/l2/staking/L2Staking.sol",
    "packages/contracts/contracts/curation/Curation.sol",
    "packages/contracts/contracts/disputes/DisputeManager.sol",
    "packages/contracts/contracts/gateway/L1GraphTokenGateway.sol",
    "packages/contracts/contracts/l2/gateway/L2GraphTokenGateway.sol",
    "packages/contracts/contracts/governance/Controller.sol",
    "packages/contracts/contracts/rewards/RewardsManager.sol",
]

# Look for: integer math, token transfer, signature use, storage patterns
print("=" * 70)
print("SEARCHING FOR BUG PATTERNS")
print("=" * 70)

for f in old_contracts:
    if not os.path.exists(f):
        continue
    with open(f) as fh:
        code = fh.read()

    # Find unsafe operations
    issues = []

    # 1) Unchecked send/transfer (Solidity 0.7.x)
    for m in re.finditer(r'\.send\s*\(', code):
        line_no = code[:m.start()].count('\n') + 1
        issues.append(f"  Line {line_no}: .send() call (Solidity 0.7)")
    for m in re.finditer(r'\.transfer\s*\(', code):
        line_no = code[:m.start()].count('\n') + 1
        issues.append(f"  Line {line_no}: .transfer() call")

    # 2) block.timestamp / block.number usage
    for m in re.finditer(r'block\.(timestamp|number)', code):
        line_no = code[:m.start()].count('\n') + 1
        # Get line content
        lines = code.split('\n')
        if line_no <= len(lines):
            line = lines[line_no-1].strip()
            if 'require(' not in line and 'assert(' not in line:
                if 'modifier' in line or 'function' in line:
                    continue
                # Skip storage access
                if 'last' in line.lower() or 'block.' in line and 'block' not in line.lower():
                    pass

    # 3) Low-level call
    for m in re.finditer(r'\.call\s*\(', code):
        line_no = code[:m.start()].count('\n') + 1
        issues.append(f"  Line {line_no}: .call() usage")

    # 4) delegatecall
    for m in re.finditer(r'delegatecall', code):
        line_no = code[:m.start()].count('\n') + 1
        issues.append(f"  Line {line_no}: delegatecall")

    # 5) tx.origin
    for m in re.finditer(r'tx\.origin', code):
        line_no = code[:m.start()].count('\n') + 1
        issues.append(f"  Line {line_no}: tx.origin usage (phishing risk)")

    # 6) assembly
    asm_count = len(re.findall(r'assembly\s*\{', code))
    if asm_count > 0:
        issues.append(f"  Has {asm_count} assembly blocks")

    # 7) Selfdestruct
    if 'selfdestruct' in code.lower():
        issues.append("  HAS selfdestruct")

    # 8) delegatecall proxies
    if 'TransparentUpgradeableProxy' in code or 'UUPS' in code:
        issues.append("  Uses upgradeable proxy pattern")

    # 9) Missing zero-address checks
    for m in re.finditer(r'function\s+(\w+)[^{]+\{\s*([^{}]*)\}', code[:5000], re.DOTALL):
        sig = m.group(1)
        body = m.group(2)
        if 'address' in sig and '_' in sig and 'non-zero' not in body and '!= address(0)' not in body and '_to' in body:
            line_no = code[:m.start()].count('\n') + 1
            if 'memory' in sig:
                continue  # skip memory addresses
            issues.append(f"  Line {line_no}: function {sig[:80]} may lack zero-address check")

    if issues:
        print(f"\n{f} ({len(issues)} potential issues):")
        for i in issues[:15]:
            print(i)

# Look for delegationPool/ratio issues
print()
print("=" * 70)
print("DELEGATION POOL ANALYSIS - looking for share manipulation")
print("=" * 70)

with open("packages/contracts/contracts/staking/libs/Stakes.sol") as f:
    stakes = f.read()
print(f"  Stakes.sol: {len(stakes.split(chr(10)))} lines")

# Find share calculation functions
for m in re.finditer(r"function\s+(\w+)\s*\([^)]*\)[^{]*\{[^}]*shares[^}]*\}", stakes):
    func = m.group(0)
    if "view" in func and len(func) < 800:
        print(f"  Found: {m.group(1)}")
        print(f"    {func[:400]}")

# Look at tokenWithdrawn / share dilution
print()
print("=" * 70)
print("REWARDS MANAGER - integer math edge cases")
print("=" * 70)

with open("packages/contracts/contracts/rewards/RewardsManager.sol") as f:
    rm = f.read()

# Find all .mul/.div/.add/.sub operations
math_ops = re.findall(r'\.(\w+)\s*\(\s*FIXED_POINT_SCALING_FACTOR', rm)
print(f"  fixed-point math ops: {len(math_ops)}")

# Find potential division-by-zero or overflow
for m in re.finditer(r'(\w+)\.div\s*\(', rm):
    line_no = rm[:m.start()].count('\n') + 1
    line = rm.split('\n')[line_no-1].strip()
    if 'require' not in rm.split('\n')[max(0,line_no-3):line_no+1][0] if line_no < len(rm.split('\n')) else '':
        pass  # Complex check, skip

# Find periods/snapshots
print()
print("=" * 70)
print("REWARDS - snapshots / state variables")
print("=" * 70)
for m in re.finditer(r'(accRewardsPerSignal|accRewardsForSubgraph|accRewardsPerAllocatedToken)\s*=\s*[^;]+;', rm):
    line_no = rm[:m.start()].count('\n') + 1
    print(f"  Line {line_no}: {m.group(0)[:200]}")

# Look at the dispute manager (always has interesting logic)
print()
print("=" * 70)
print("DISPUTE MANAGER - look for arbitration logic bugs")
print("=" * 70)
with open("packages/contracts/contracts/disputes/DisputeManager.sol") as f:
    dm = f.read()
print(f"  {len(dm.split(chr(10)))} lines")

# Find functions
for m in re.finditer(r"function\s+(\w+)\s*\(([^)]*)\)\s+([^{]+)\s*\{", dm):
    name, args, mods = m.group(1), m.group(2), m.group(3)
    if 'override' in mods and 'external' in mods:
        print(f"  external override: {name}({args.strip()}) {mods.strip()}")
