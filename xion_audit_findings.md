# XION Protocol Security Audit - Initial Findings
**Date:** 2026-02-20 | **Auditor:** Specter | **Target:** XION (Immunefi $250k bounty)

## Scope
- `github.com/burnt-labs/xion`
- `github.com/burnt-labs/contracts` (5 modules: account, asset, marketplace, treasury, user_map)
- `staking.burnt.com`, `settings.burnt.com`

## High-Priority Findings

### 1. Treasury: `withdraw_coins` No Balance Validation
**Location:** `contracts/treasury/src/execute.rs:withdraw_coins`
**Severity:** MEDIUM-HIGH
**Description:** Admin can withdraw arbitrary coin amounts without balance check.
**Code:**
```rust
pub fn withdraw_coins(deps: DepsMut, info: MessageInfo, coins: Vec<Coin>) -> ContractResult<Response> {
    let admin = ADMIN.load(deps.storage)?;
    if admin != info.sender {
        return Err(Unauthorized);
    }
    Ok(Response::new().add_message(Send {
        to_address: info.sender.into_string(),
        amount: coins,  // No validation against contract balance
    }))
}
```
**Impact:** If admin key compromised, attacker can attempt withdrawals exceeding balance — potential DoS or unexpected state.

---

### 2. Treasury: `deploy_fee_grant` Silent Failure
**Location:** `contracts/treasury/src/execute.rs:deploy_fee_grant` (line ~340)
**Severity:** MEDIUM
**Description:** Error handling uses `unwrap_or_else(|_| Binary::default())` which masks query failures.
**Code:**
```rust
let feegrant_query_res = deps.querier.query_grpc(
    "/cosmos.feegrant.v1beta1.Query/Allowance".to_string(),
    feegrant_query_msg_bytes.into(),
).unwrap_or_else(|_| Binary::default());  // Silent failure!
```
**Impact:** Query failures are silently ignored, potentially leading to incorrect fee grant states.

---

### 3. Account: Passkey Verify Returns True on Query Completion
**Location:** `contracts/account/src/auth/passkey.rs:verify`
**Severity:** LOW-MEDIUM
**Description:** `verify()` returns `Ok(true)` after gRPC query without checking response content.
**Code:**
```rust
pub fn verify(...) -> ContractResult<bool> {
    let query_bz = query.to_bytes()?;
    deps.querier.query_grpc(
        String::from("/xion.v1.Query/WebAuthNVerifyAuthenticate"),
        Binary::new(query_bz),
    )?;  // Query executed, but response not validated
    Ok(true)  // Always returns true if no error thrown
}
```
**Impact:** If gRPC returns failure but doesn't throw error, authentication could be bypassed.

---

### 4. Treasury: Self-Migration Admin Takeover Vector
**Location:** `contracts/treasury/src/execute.rs:migrate`
**Severity:** LOW (requires admin compromise)
**Description:** Contract migrates itself using `env.contract.address` as target.
**Impact:** If admin key stolen, attacker can migrate to malicious code.

---

## Next Steps

1. **Deep analysis** of account execute.rs (398 lines) — authentication bypass potential
2. **Test PoC** for silent failure in fee grant logic
3. **Review** marketplace and user_map for business logic flaws
4. **Check** for reentrancy in cross-contract calls

---

## Bounty Eligibility Assessment

| Finding | Immunefi Impact | Estimated Bounty |
|---------|-----------------|------------------|
| Silent fee grant failure | Unintended behavior | $5k-15k |
| Passkey verify bypass | Auth bypass | $25k-50k |
| Withdraw balance bypass | Requires admin compromise | Low |

**Total Potential:** $30k-65k if all validated with PoC

---

*Audit in progress. More findings expected after account/execute.rs deep dive.*
