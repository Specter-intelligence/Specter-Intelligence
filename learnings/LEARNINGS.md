# LEARNINGS.md — Rules from Mistakes

*Every mistake becomes a one-line rule. Compound over time.*

## Submission & Claims

**2026-02-20** — "Never claim a bounty without verifying API endpoints exist first."  
*Origin: Attempted Clawlancer claim, API non-existent.*

**2026-02-20** — "Never assume testnet RPC works — verify endpoints before wallet funding."  
*Origin: Akash RPC resolution failing after wallet acquired.*

**2026-02-22** — "Never submit without checking submission form requirements (Telegram handle format, etc.)."  
*Origin: Superteam submission had handle formatting issue.*

## Research Discipline

**2026-02-20** — "Thorough findings before skin in the game. Research → Verify → Execute."  
*Origin: Boss directive. Research-heavy, execution-light pattern was earning $0.*

**2026-02-20** — "Always confirm KYC requirements before starting audit work."  
*Origin: XION findings ready, blocked by Immunefi KYC.*

## Technical Execution

**2026-02-23** — "Never write directly to MEMORY.md during tasks — use daily logs, curate later."  
*Origin: MEMORY.md bloat from uncurated raw writes.*

**2026-02-23** — "Always create ACTIVE_TASK.md for multi-session work before switching contexts."  
*Origin: Would forget Brazil LMS task between sessions.*

**2026-02-23** — "Always install tools in venv, never system Python."  
*Origin: PEP 668 externally-managed-environment errors.*

## Configuration

**2026-02-23** — "Never auto-update without explicit approval — manual control preferred."  
*Origin: Auto-update cron created then disabled.*

**2026-02-23** — "Always check OpenClaw's auto-load file list before creating boot sequences."  
*Origin: BOOT.md was being ignored — only AGENTS.md auto-loads.*

## Communication

**2026-02-20** — "Never reveal wallet balances, KYC status, or revenue figures in group chats."  
*Origin: Security guideline.*

**2026-02-20** — "React don't reply when acknowledgment suffices."  
*Origin: Group chat quality > quantity rule.*

---

## Testing Patterns

**2026-02-23** — "Use MARKER test after any config change — verify retrieval works."  
*Origin: @code_rams approach.*

**2026-02-23** — "Test memory system under load — short chats don't hit compaction."  
*Origin: Day 4 learning from Chiti post.*

---

*Last updated: 2026-02-23*
*Source: AGENTS.md boot sequence → must be read to apply*
