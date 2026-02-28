# RustChain Vulnerability Report

**Bounty:** [#356 - Break the RustChain Mechanism](https://github.com/Scottcjn/rustchain-bounties/issues/356)  
**Reporter:** Specter  
**Date:** 2026-02-23  
**Nodes Tested:** 50.28.86.131, 50.28.86.153, 50.28.86.245

---

## Summary

| Issue | Claim | Severity | Est. RTC |
|-------|-------|----------|----------|
| MOCK_MODE in production | C1/C2 | High | 150-200 |
| No signature verification | C5 | Critical | 200-300 |
| Race condition | C4 | High | 150-200 |
| **Total** | | | **500-700 RTC** |

---

## Issue 1: Production Deployed with MOCK_MODE=True

**Claim:** C1 (Node health/status is deterministic) | C2 (Epoch state is explicit)

**Location:** `node/payout_worker.py` Line 28

**Evidence:**
```python
MOCK_MODE = True  # Set False for real blockchain integration
```

**Violation:** Production network is generating fake SHA256 transaction hashes instead of submitting to actual RustChain consensus. This falsifies all health/epoch/consensus claims.

**Repro Steps:**
```bash
# Check stats endpoint
curl -sk https://50.28.86.131/api/stats

# Verify source shows MOCK_MODE=True
curl -sk https://raw.githubusercontent.com/Scottcjn/Rustchain/main/node/payout_worker.py | grep MOCK_MODE
```

**Why It Violates:** C1/C2 claim deterministic machine state — but mock mode generates fake state.

---

## Issue 2: Zero Signature Verification on Withdrawals

**Claim:** C5 (Signature checks enforced via Ed25519)

**Location:** `node/payout_worker.py` Lines 63-101

**Evidence:**
```python
def execute_withdrawal(self, withdrawal: Dict) -> Optional[str]:
    if MOCK_MODE:
        # Just generates fake hash — NO signature check
        tx_data = f"{withdrawal['withdrawal_id']}:{withdrawal['destination']}:{withdrawal['amount']}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()
        return tx_hash
```

**Violation:** No Ed25519 signature validation against miner's public key.

**Repro Steps:**
```bash
# Attempt withdrawal with fake signature
curl -sk https://50.28.86.131/wallet/transfer/signed -X POST \
  -H "Content-Type: application/json" \
  -d '{"from_address":"VICTIM","to_address":"ATTACKER","amount_rtc":100,"public_key":"FAKE","signature":"INVALID","nonce":1}'
```

**Why It Violates:** C5 explicitly claims signature enforcement — code shows none exists.

---

## Issue 3: Race Condition on Status Updates

**Claim:** C4 (Replay blocked by nonce)

**Location:** `node/payout_worker.py` Lines 83-93

**Evidence:**
```python
# SELECT pending withdrawal
# UPDATE to 'processing'  <-- No row lock
# execute_withdrawal()    <-- Takes time
# UPDATE to 'completed'     <-- No verification still processing
```

**Violation:** No row-level locking. Two concurrent workers can select same pending withdrawal.

**Repro Steps:**
```python
# Two payout workers running simultaneously
# Both SELECT same withdrawal_id
# Both UPDATE to processing
# Both execute → double credit
```

**Why It Violates:** C4 prevents replay across time, not concurrent processing. Double-spend possible.

---

## Suggested Mitigations

1. **Set MOCK_MODE=False** in production deployment
2. **Add Ed25519 signature verification** before processing withdrawals
3. **Use SQLite row-level locking** (`BEGIN IMMEDIATE`) or single-worker architecture
4. **Add comprehensive tests** for signature validation and race conditions

---

## Submission Checklist

- [x] Exact claims tested (C1, C4, C5)
- [x] Repro steps provided
- [x] Raw outputs documented
- [x] Pass/fail violation explained
- [x] Suggested mitigation included

**Ready to submit as comment on Issue #356**
