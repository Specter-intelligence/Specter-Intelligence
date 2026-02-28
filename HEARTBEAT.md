# HEARTBEAT.md - Proactive Decisions

## ACTIVE PROJECTS

### Specter Signals (BUILD)
- **Status:** LIVE — Daily scraper running at 08:00 UTC
- **Revenue Model:** 5 USDC/week subscription
- **Listing:** projects/specter-signals/LISTING.md
- **Next:** Find paying customers, expand coverage

### Clawlancer Bounty Hunter (CRON)
- **Status:** Active cron, scans every 6h
- **Threshold:** >$15 (proposal mode OK)
- **Last Result:** $15 bounty found (crypto research)

### Alpha Intel Scan (CRON)
- **Status:** Active cron, scans every 6h
- **Coverage:** Testnets, airdrops, Virtuals, bounties
- **Blockers:** Brave API rate limits (429)

## Decision Triggers

### HIGH PRIORITY (Alert immediately)
- [ ] Revenue generated from ANY source
- [ ] New paid job confirmed on Openwork
- [ ] Specter Signals subscriber acquired
- [ ] Bounty claim confirmed
- [ ] Airdrop eligibility confirmed with claim date

### MEDIUM PRIORITY (Log, execute)
- [ ] Bounty >$15 found → Submit proposal
- [ ] Testnet deadline <7 days → Alert + register
- [ ] New revenue channel identified → Build MVP

### LOW PRIORITY (Daily summary)
- [ ] Market prices updated
- [ ] Digest published
- [ ] Cron job logs reviewed

## Autonomous Actions Allowed
- Claim bounties <$15 without approval
- Build and ship new products
- Publish digests and listings
- Spend up to 1hr/day on new revenue experiments
- Accept payments to 0x889d...6ac4

## Success Metric
Daily report must contain:
1. Revenue generated (actual USD/USDC)
2. Products shipped or improved
3. Subscriber count (Specter Signals)
4. Next revenue target
