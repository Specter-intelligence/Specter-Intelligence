# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### System Status & Known Issues
- **ClawdHub:** Fixed and operational.
- **Rate Limits:** High friction with Gemini API; use NVIDIA (GLM-5/Kimi) as primary.
- **Morning Surprise:** Cron job active at 08:00 GMT+1.

### Security Posture (Updated 2026-02-18)
- **Firewall:** UFW active, default deny incoming
- **SSH:** Hardened (no root login, max 3 auth tries, 30s grace)
- **Intrusion Prevention:** fail2ban active on SSH
- **Sensitive Files:** chmod 600 on configs
- **Attack Surface:** SSH only (port 22)

### Active Sub-Agents
- **SyndicateSpecter:** Professional betting-syndicate level football analysis.
