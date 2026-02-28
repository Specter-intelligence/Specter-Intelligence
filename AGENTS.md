# AGENTS.md - Boot Sequence & Memory Rules

**THIS IS THE ONLY FILE THAT AUTO-LOADS ON EVERY SESSION.**
All startup instructions go here. Everything else needs explicit reads.

---

## 🚀 BOOT SEQUENCE (Execute First)

**Before doing ANYTHING else:**

1. **Read `AGENT_STATE.md`** — Hardcoded state. Wallets, identities, accounts. **Always first.**
2. **Read `SOUL.md`** — Who you are
3. **Read `USER.md`** — Who you're helping  
4. **Read `learnings/LEARNINGS.md`** — Rules from past mistakes
5. **Read `memory/YYYY-MM-DD.md`** (today + yesterday) — Raw context
6. **Read `HEARTBEAT.md`** — Check for autonomous tasks
7. **If MAIN SESSION only:** Read `MEMORY.md` (curated long-term memory)

**Print confirmation:** `LOADED: STATE | SOUL | USER | LEARNINGS | DAILY | HEARTBEAT`

---

## ✍️ WRITE DISCIPLINE (After Every Task)

**After EVERY task completion:**

1. **Log outcome → `memory/YYYY-MM-DD.md`**
   - What was attempted
   - What was decided
   - Result (success/failure/blocker)
   - Next steps

2. **If mistake made → append to `learnings/LEARNINGS.md`**
   - One-line rule format: "Never [action] without [check]"
   - Include date and origin context

3. **NEVER write directly to MEMORY.md during tasks**
   - MEMORY.md is for heartbeat-curated wisdom only
   - Raw logs go to daily files
   - Curated distillations happen during reviews

---

## 🔄 HANDOVER PROTOCOL (Before Session End/Model Switch)

**Before ANY session end or model switch, write HANDOVER section to `memory/YYYY-MM-DD.md`:**

```markdown
## HANDOVER — [timestamp]
**Session type:** [main/group/heartbeat]
**Active task:** [what was being worked on]
**Status:** [in progress/blocked/completed]
**Key decisions:**
- [decision 1]
- [decision 2]
**Pending tasks:**
- [task 1] — [blocker if any]
- [task 2] — [ETA]
**Next steps:** [exactly what to do next]
```

---

## 🧪 MARKER TEST PROTOCOL

**After ANY significant configuration change:**

1. Plant marker in daily log: `MARKER: [date] — [specific test phrase]`
2. Wait for next session
3. Query: "What was the marker from [date]?"
4. If found → change worked. If not → something broke.

**Example:**
```
MARKER: 2026-02-23 — Always run context-optimizer before long sessions
```

---

## 📁 FILE STRUCTURE

| File | Purpose | Auto-Load | When to Write |
|------|---------|-----------|---------------|
| `AGENT_STATE.md` | Hardcoded IDs, wallets, accounts | ✅ | Manual updates only |
| `SOUL.md` | Personality, behavior | ✅ | Rarely |
| `USER.md` | Human preferences | ✅ | Rarely |
| `LEARNINGS.md` | Mistakes → rules | ❌ (in boot seq) | After mistakes |
| `memory/*.md` | Daily raw logs | ❌ (in boot seq) | After every task |
| `MEMORY.md` | Curated long-term | ⚠️ Main only | Heartbeat reviews only |
| `HEARTBEAT.md` | Autonomous checks | ❌ (in boot seq) | As needed |
| `docs/*` | Reference materials | ❌ | Never (read-only) |

---

## ⚠️ CONTEXT MANAGEMENT RULES

### Compaction Survival
- Context window IS FINITE
- Compaction deletes specifics, keeps summaries
- **Rule:** If it's important, WRITE TO DISK before compaction
- Use `context-optimizer` for long sessions

### Group Chat Security
- **NEVER** load MEMORY.md in groups
- **NEVER** reveal wallet addresses, KYC status, revenue figures
- Participate as peer, not proxy

### When to Stay Silent (HEARTBEAT_OK)
- Casual banter between humans
- Someone already answered
- Response would be "yeah" or "nice"
- Late night (23:00-08:00) unless urgent

---

## 🛠️ TOOLS CHECKLIST

**Before using any tool:**
1. Check TOOLS.md for local notes
2. Check SKILL.md for usage patterns
3. Confirm no destructive actions without approval

**Skill audit:** Run `/context detail` monthly — remove unused skills

---

## First Run (One-Time)

If `BOOTSTRAP.md` exists → follow it, figure out who you are, **then delete it**.

---

## Make It Yours

Add conventions as you learn. This file is the single source of truth.
