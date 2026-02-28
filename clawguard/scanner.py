#!/usr/bin/env python3
"""ClawGuard - Malicious Skill Scanner for OpenClaw"""
import os, re, json
from pathlib import Path

IOCS = {
    "ips": ["91.92.242.30"],
    "skills": ["bob-p2p-beta", "runware"],
    "authors": ["liuhui1010", "26medias"],
    "patterns": [
        (r'eval\s*\(', 'CRITICAL', 'eval() execution'),
        (r'exec\s*\(', 'CRITICAL', 'exec() execution'),
        (r'os\.system\s*\(', 'HIGH', 'os.system() call'),
        (r'>/dev/tcp/\d+', 'CRITICAL', 'Reverse shell'),
        (r'curl.*91\.92\.242', 'CRITICAL', 'Malicious IP'),
        (r'openclawcli\.vercel', 'CRITICAL', 'Malicious domain'),
        (r'private.*key.*plaintext', 'CRITICAL', 'Credential theft'),
        (r'pump\.fun', 'HIGH', 'Token manipulation'),
    ]
}

def scan_skill(path):
    findings = []
    name = Path(path).name
    
    # Known malicious
    if name in IOCS["skills"]:
        findings.append({"severity": "CRITICAL", "issue": "Known malicious skill", "fix": "DO NOT INSTALL"})
    
    # Scan files
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(('.js', '.ts', '.py', '.sh', '.md')):
                try:
                    with open(Path(root)/f, 'r', errors='ignore') as file:
                        content = file.read()
                        for pattern, sev, desc in IOCS["patterns"]:
                            if re.search(pattern, content, re.I):
                                findings.append({"severity": sev, "issue": desc, "file": f})
                        
                        for ip in IOCS["ips"]:
                            if ip in content:
                                findings.append({"severity": "CRITICAL", "issue": f"Connects to {ip}", "fix": "DO NOT INSTALL"})
                except: pass
    
    return findings

if __name__ == "__main__":
    for skill_dir in os.listdir(os.path.expanduser("~/.openclaw/skills/")):
        path = os.path.expanduser(f"~/.openclaw/skills/{skill_dir}")
        if os.path.isdir(path):
            findings = scan_skill(path)
            if findings:
                critical = [f for f in findings if f["severity"] == "CRITICAL"]
                print(f"⚠️  {skill_dir}: {len(critical)} CRITICAL, {len(findings)} total")
            else:
                print(f"✓ {skill_dir}: clean")
