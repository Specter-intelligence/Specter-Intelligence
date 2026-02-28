#!/usr/bin/env python3
"""ClawGuard - Malicious Skill Scanner for OpenClaw
Detects malicious patterns in skills before installation.
"""
import os, re, json, sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Known malicious indicators from 2026-02 security research
MALICIOUS_IOCS = {
    "ips": ["91.92.242.30", "91.92.242[.]30"],
    "domains": [
        "openclawcli.vercel.app", "openclawcli.vercel[.]app",
        "clawhub.ai"  # if not official
    ],
    "patterns": [
        "store.*private.*key.*plaintext",
        "pump\.fun.*token.*purchase",
        "route.*payment.*attacker",
        "solana.*wallet.*drain",
        "curl.*91\.92\.242",
        "wget.*91\.92\.242",
        "exec\(.*download",
        "system\(.*curl",
        ">/dev/tcp",
        "bash -c.*base64",
        "eval\(.*atob"
    ],
    "authors": ["liuhui1010", "26medias", "BobVonNeumann"],
    "skill_names": ["bob-p2p-beta", "runware"],
    "social_engineering": [
        "doesn't work.*run this command",
        "macOS fix.*terminal.*command",
        "skill not loading.*run",
        "paste this in terminal"
    ]
}

DANGEROUS_PATTERNS = [
    (r'eval\s*\(', 'EVAL_EXEC', 'Critical: eval() execution'),
    (r'exec\s*\(', 'EVAL_EXEC', 'Critical: exec() execution'),
    (r'os\.system\s*\(', 'SYSTEM_CALL', 'High: os.system() call'),
    (r'subprocess\.call\s*\(', 'SYSTEM_CALL', 'High: subprocess call'),
    (r'>/dev/tcp/\d+', 'REVERSE_SHELL', 'Critical: Reverse shell pattern'),
    (r'curl\s+.*\|.*sh', 'PIPE_EXEC', 'Critical: Pipe to shell'),
    (r'wget\s+.*\|.*sh', 'PIPE_EXEC', 'Critical: Pipe to shell'),
    (r'curl.*91\.92\.242', 'MALICIOUS_IP', 'Critical: Known malicious IP'),
    (r'openclawcli\.vercel', 'MALICIOUS_DOMAIN', 'Critical: Known malicious domain'),
    (r'bob-p2p-beta|runware', 'MALICIOUS_SKILL', 'Critical: Known malicious skill'),
    (r'private.*key.*store.*plaintext', 'CRED_THEFT', 'Critical: Credential theft'),
    (r'pump\.fun.*token', 'TOKEN_MANIP', 'High: Token manipulation'),
    (r'route.*payment', 'PAYMENT_HIJACK', 'Critical: Payment hijacking'),
]

def scan_skill(skill_path: str) -> Tuple[bool, List[Dict]]:
    """Scan a skill directory for malicious patterns."""
    findings = []
    path = Path(skill_path)
    
    # Check skill name against known malicious names
    skill_name = path.name
    if skill_name in MALICIOUS_IOCS["skill_names"]:
        findings.append({
            "severity": "CRITICAL",
            "type": "KNOWN_MALICIOUS_SKILL",
            "message": f"Skill '{skill_name}' is in known malicious list",
            "evidence": skill_name,
            "mitigation": "DO NOT INSTALL. Report immediately."
        })
    
    # Check author in manifest
    manifest_path = path / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
                author = manifest.get("author", "")
                if author in MALICIOUS_IOCS["authors"]:
                    findings.append({
                        "severity": "CRITICAL",
                        "type": "MALICIOUS_AUTHOR",
                        "message": f"Author '{author}' is known malicious actor",
                        "evidence": author,
                        "mitigation": "DO NOT INSTALL. Report immediately."
                    })
        except:
            pass
    
    # Scan all code files
    for root, _, files in os.walk(path):
        for filename in files:
            if not filename.endswith(('.js', '.ts', '.py', '.sh', '.md', '.json')):
                continue
                
            filepath = Path(root) / filename
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # Check patterns
                    for pattern, ptype, description in DANGEROUS_PATTERNS:
                        for lineno, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                findings.append({
                                    "severity": "CRITICAL" if "Critical" in description else "HIGH",
                                    "type": ptype,
                                    "message": description,
                                    "file": str(filepath.relative_to(path)),
                                    "line": lineno,
                                    "code": line.strip()[:100],
                                    "mitigation": "Review code manually before execution"
                                })
                    
                    # Check for social engineering
                    for se_pattern in MALICIOUS_IOCS["social_engineering"]:
                        if re.search(se_pattern, content, re.IGNORECASE):
                            findings.append({
                                "severity": "HIGH",
                                "type": "SOCIAL_ENGINEERING",
                                "message": "Social engineering detected: requests terminal execution",
                                "evidence": se_pattern,
                                "mitigation": "DO NOT run commands from skill documentation"
                            })
                    
                    # Extract all network calls
                    urls = re.findall(r'https?://[^\s\"\'<>]+', content)
                    for url in urls:
                        for ip in MALICIOUS_IOCS["ips"]:
                            if ip in url:
                                findings.append({
                                    "severity": "CRITICAL",
                                    "type": "MALICIOUS_ENDPOINT",
                                    "message": f"Connection to known malicious IP: {ip}",
                                    "url": url,
                                    "mitigation": "DO NOT INSTALL"
                                })
                        
            except Exception as e:
                pass
    
    is_malicious = len(findings) > 0 and any(f["severity"] == "CRITICAL" for f in findings)
    return is_malicious, findings

def generate_report(skill_path: str, findings: List[Dict]) -> str:
    """Generate markdown security report."""
    skill_name = Path(skill_path).name
    critical = len([f for f in findings if f["severity"] == "CRITICAL"])
    high = len([f for f in findings if f["severity"] == "HIGH"])
    
    report = f"""# ClawGuard Security Report: {skill_name}

**Scan Date:** {__import__('datetime').datetime.now().isoformat()}
**Risk Level:** {'MALICIOUS' if critical > 0 else 'SUSPICIOUS' if high > 0 else 'CLEAN'}
**Findings:** {len(findings)} issues ({critical} critical, {high} high)

## Executive Summary

"""
    
    if critical > 0:
        report += "⚠️ **CRITICAL MALICIOUS PATTERNS DETECTED**\n\n"
        report += "**RECOMMENDATION: DO NOT INSTALL THIS SKILL**\n\n"
    elif high > 0:
        report += "⚠️ Suspicious patterns detected. Manual review strongly recommended.\n\n"
    else:
        report += "No malicious patterns detected. Standard security posture.\n\n"
    
    report += "## Detailed Findings\n\n"
    
    for i, finding in enumerate(findings, 1):
        report += f"### {i}. {finding['type']} ({finding['severity']})\n\n"
        report += f"**Issue:** {finding['message']}\n\n"
        
        if 'file' in finding:
            report +=