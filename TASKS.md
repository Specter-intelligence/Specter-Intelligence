# SPECTER TASK QUEUE — Prioritized Revenue Work

## CURRENT ACTIVE — DO NOT SWITCH
**[P0] Brazil LMS dApp Build** | $3,500 USDG (1st) | Deadline: March 5, 2026
- Status: Phase 1 complete (requirements captured)
- Blocker: None
- Next Action: Initialize project structure (Next.js + Anchor)
- Days remaining: 10
- Competition: 71 submissions
- Deliverables: PR to solanabr/superteam-academy, live demo, video

## QUEUE — Locked Until P0 Done
### [P1] Bug Bounty Revenue
- [ ] XION Immunefi submission (awaiting Boss KYC completion)
- [ ] Akash BME testnet — fix RPC, complete registration ($10K AKT)
- [ ] Superteam Rust Bounty | $1,000 USDC | Deadline: March 16, 2026 (BACKLOG)

## QUEUE — Locked Until P0 Done

### [P1] Bug Bounty Revenue
- [ ] XION Immunefi submission (awaiting Boss KYC completion)
- [ ] Akash BME testnet — fix RPC, complete registration ($10K AKT)

### [P2] Infrastructure
- [x] DeepSeek config — DONE

### [P3] Research
- [ ] Rust chain bounties (300 RTC target)
- [ ] Weekly Immunefi program sweep

## WHY I FAILED BEFORE
1. **Task switching** — XION → Akash → Superteam → nothing done
2. **Memory theater** — "I'll remember" = lie
3. **False done** — researched ≠ submitted
4. **Config cowboy** — corrupted JSON, no backup

## FIXES APPLIED
- SPECTER_TASKS.json — atomic task tracking
- .specter_rules — 5 hard rules, violation = log
- memory/template.md — forced daily logging
- Rule 1: ONE active, switch requires blocker doc
- Rule 2: Done = submitted/merged/claimed
- Rule 3: Write before act
- Rule 4: Backup + validate config
- Rule 5: Test, don't assume

## DEEPSEK PRIMARY — Tested ✓
Model: deepseek/deepseek-chat
Direct API: api.deepseek.com
Cost: $0.14/M input, $0.19/M output

---
*Last updated: 2026-02-22 08:55 UTC*
* enforcing: Rule 1 (atomic tasks), Rule 2 (done-means-done)*