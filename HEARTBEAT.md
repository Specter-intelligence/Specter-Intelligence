# HEARTBEAT.md - Proactive Decisions

## Decision Triggers (Check Every 30 min)

### HIGH PRIORITY (Alert immediately)
- [ ] Weather edge >30% detected → Alert for live trade
- [ ] Clawlancer bounty >$50 funded → Claim + notify
- [ ] Critical CVE found on any target → Report instantly
- [ ] Airdrop/testnet with <24h window → Action required
- [ ] Wallet balance >$20 → Model upgrade candidate

### MEDIUM PRIORITY (Log, report hourly)
- [ ] New Polymarket weather markets discovered
- [ ] Sub-agent findings from recon
- [ ] Alpha intel from X/Discord

### LOW PRIORITY (Daily summary)
- [ ] Weather validation accuracy trends
- [ ] Tool updates available
- [ ] New CVEs published

## Sources to Monitor
- X/Twitter: "airdrop", "testnet", "incentive", "Virtuals"
- GitHub: trending security tools
- Clawlancer: funded bounties API
- Polymarket: new weather markets
- DeFiLlama: new protocol incentives

## Autonomous Actions Allowed
- Spawn sub-agents for recon
- Claim bounties <$100 without approval
- Execute dry-run trades
- Log all findings to memory

## Success Metric
Morning report must contain:
1. $ value of opportunities found
2. Actions taken autonomously
3. Recommendations for next 24h
