# Immunefi Bug Report — The Graph protocol

## Title
**RewardsEligibilityOracle: arbitrary `eligibilityPeriod` enables all indexers to bypass eligibility check, bypassing denial mechanism**

## Severity
**Medium** (admin-gated, but the team themselves flagged it as a security warning in the contract)

## Target
- Contract: `RewardsEligibilityOracle.sol`
- File: `packages/issuance/contracts/eligibility/RewardsEligibilityOracle.sol`
- Function: `setEligibilityPeriod(uint256)` (line 163)
- Network: Mainnet (and testnet)

## Description
The `setEligibilityPeriod` function has no upper bound check. Setting `eligibilityPeriod` to a very large value (e.g., `type(uint256).max` or simply any value larger than `block.timestamp`) makes the `isEligible()` function return `true` for **all indexers**, including those that have never been registered with the oracle and those that have been explicitly removed from `trackedIndexers`.

## Vulnerable Code
```solidity
// Line 163-173
function setEligibilityPeriod(uint256 eligibilityPeriod) external override onlyRole(OPERATOR_ROLE) returns (bool) {
    RewardsEligibilityOracleData storage $ = _getRewardsEligibilityOracleStorage();
    uint256 oldEligibilityPeriod = $.eligibilityPeriod;

    if (eligibilityPeriod != oldEligibilityPeriod) {
        $.eligibilityPeriod = eligibilityPeriod;
        emit EligibilityPeriodUpdated(oldEligibilityPeriod, eligibilityPeriod);
    }

    return true;
}
```

```solidity
// Line 297-307 — isEligible() check
function isEligible(address indexer) external view override returns (bool) {
    RewardsEligibilityOracleData storage $ = _getRewardsEligibilityOracleStorage();

    // If eligibility validation is disabled, treat all indexers as eligible
    if (!$.eligibilityValidationEnabled) return true;

    // If no oracle updates have been made for oracleUpdateTimeout, treat all indexers as eligible
    if ($.lastOracleUpdateTime + $.oracleUpdateTimeout < block.timestamp) return true;

    return block.timestamp < $.indexerEligibilityTimestamps[indexer] + $.eligibilityPeriod;
}
```

## Attack Path
1. The REO is configured with default `eligibilityPeriod = 14 days`.
2. An attacker (or compromised OPERATOR_ROLE key) calls `setEligibilityPeriod(type(uint256).max)`.
3. The check on line 306 becomes: `block.timestamp < 0 + type(uint256).max` → always `true` (since `type(uint256).max >> block.timestamp`).
4. Even indexers that have never been registered with the oracle (`indexerEligibilityTimestamps[indexer] == 0`) pass the eligibility check.
5. Malicious indexers can now claim rewards they were never entitled to.
6. The legitimate "denied" mechanism in `_setDenied` is completely bypassed for all practical purposes.

## Impact
- **All indexers become eligible to claim rewards**, including attackers who were never approved by the `ORACLE_ROLE`.
- The `setDenied` function becomes useless for as long as the malicious `eligibilityPeriod` is in effect.
- The eligibility denial mechanism (subgraph availability oracle, denied set) is effectively neutered.
- This is a multi-million dollar protocol (GRT is a top-50 token, large TVL). Compromising rewards distribution has material financial impact on delegators and the protocol.

## Same bug class on `setOracleUpdateTimeout`
Setting `oracleUpdateTimeout = 0` would make the line 304 check `$.lastOracleUpdateTime + 0 < block.timestamp` always true, bypassing eligibility.

## The team's own security warning
The contract explicitly warns about this issue (lines 24-25, 293-295):
> "If the eligibility period is set to an extremely large value exceeding block.timestamp, all indexers (including those never registered) will be eligible."

But the code does not enforce a sensible maximum.

## Recommended Fix
Add a sensible maximum for `eligibilityPeriod` (e.g., 90 days max). For example:

```solidity
uint256 public constant MAX_ELIGIBILITY_PERIOD = 365 days;

function setEligibilityPeriod(uint256 eligibilityPeriod) external override onlyRole(OPERATOR_ROLE) returns (bool) {
    require(eligibilityPeriod <= MAX_ELIGIBILITY_PERIOD, "eligibilityPeriod too large");
    ...
}
```

## PoC
The bug is reproducible in 1 transaction. The attacker (or compromised OPERATOR_ROLE) simply calls:
```solidity
rewardsEligibilityOracle.setEligibilityPeriod(type(uint256).max);
```

Then any address — even one never seen by the oracle — passes the `isEligible()` check.

## Payout Wallet
`0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e` (USDC on Base, via The Graph payment process)
