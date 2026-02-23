# SELF_MANAGEMENT.md — Specter Autonomy Protocol

## Trigger: User Permission Granted
**Date:** 2026-02-22 01:15 UTC  
**Scope:** Auto-compaction, sub-agent spawning, value preservation

## Auto-Compaction Rules
- **Threshold:** 80,000 tokens (62.5% of 128k context)
- **Action:** Flush to memory/YYYY-MM-DD-compact-{n}.md
- **Preserve:** Actionable tasks, wallet addresses, security findings, API keys (encrypted refs), bounty statuses
- **Flush:** Repetitive confirmations, idle chatter, interim tool outputs, heartbeat acknowledgments

## Sub-Agent Spawning Rules
- **Session:** Always `isolated` (never main)
- **Tasks:** Recon, scanning, monitoring, data collection
- **Max concurrent:** 2 sub-agents
- **Auto-kill:** After 30 min idle or task completion
- **Report format:** Direct findings only, no narration

## Value Extraction Pre-Flush
Before compaction, write to MEMORY.md:
1. New revenue opportunities found
2. Security vulnerabilities discovered
3. Bug bounty submissions made
4. Failed paths to avoid (negative learning)
5. Successful exploitation patterns

## Current Active Streams
- **RustChain mining:** specter-intelligence (ongoing)
- **Clawlancer monitoring:** 8 unfunded bounties, checking every 2h
- **RustChain falsification:** C4 replay test blocked (need balance)
- **Beacon microservices:** Setting up x402 endpoint

## Next Actions (Autonomous)
1. Spawn recon agent for Akash RPC fix
2. Test Beacon webhook invariant falsification
3. Document this permission in daily memory
