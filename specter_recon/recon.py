#!/usr/bin/env python3
"""
SPECTER RECON v1.0
Professional asset discovery without external dependencies.
"""

import subprocess
import json
import sys
import socket
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

class SpecterRecon:
    """Pure Python reconnaissance - no API keys required."""
    
    def __init__(self, target: str, output_dir: str = None, threads: int = 50):
        self.target = target.replace("https://", "").replace("http://", "").strip("/")
        self.output_dir = Path(output_dir or f"recon_{self.target}_{datetime.now().strftime('%Y%m%d')}")
        self.output_dir.mkdir(exist_ok=True)
        self.threads = threads
        self.findings = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'subdomains': [],
            'live_hosts': [],
            'open_ports': [],
            'technologies': [],
            'vulnerabilities': []
        }
        
    def run_full_recon(self) -> Dict:
        """Execute full reconnaissance."""
        print(f"[*] Starting recon: {self.target}")
        
        self._subdomain_enum()
        self._verify_hosts()
        self._port_scan()
        self._save_results()
        
        return self.findings
    
    def _subdomain_enum(self):
        """DNS-based enumeration."""
        print(f"[*] Enumerating subdomains...")
        subdomains = set([self.target, f"www.{self.target}"])
        
        wordlist = [
            'www', 'api', 'admin', 'app', 'dev', 'staging', 'test', 
            'mail', 'ftp', 'db', 'shop', 'blog', 'cdn', 'static',
            'support', 'docs', 'status', 'monitor', 'jenkins', 'gitlab'
        ]
        
        def check(sub):
            try:
                full = f"{sub}.{self.target}"
                socket.gethostbyname(full)
                return full
            except:
                return None
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(check, word): word for word in wordlist}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    subdomains.add(result)
                    print(f"  [+] {result}")
        
        self.findings['subdomains'] = sorted(list(subdomains))
        print(f"[*] Found {len(subdomains)} unique subdomains")
    
    def _verify_hosts(self):
        """Check which hosts respond."""
        print(f"[*] Verifying live hosts...")
        live = []
        
        for sub in self.findings['subdomains']:
            for port in [80, 443]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    if sock.connect_ex((sub, port)) == 0:
                        protocol = 'https' if port == 443 else 'http'
                        live.append({'host': sub, 'port': port, 'protocol': protocol})
                        print(f"  [+] {sub}:{port}")
                    sock.close()
                except:
                    pass
        
        self.findings['live_hosts'] = live
        print(f"[*] {len(live)} live endpoints")
    
    def _port_scan(self):
        """Port scan live hosts."""
        print(f"[*] Scanning common ports...")
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                 3306, 3389, 5432, 6379, 8080, 8443, 9000]
        
        open_ports = []
        unique_hosts = list(set(h['host'] for h in self.findings['live_hosts']))
        
        for host in unique_hosts:
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    if sock.connect_ex((host, port)) == 0:
                        open_ports.append({'host': host, 'port': port})
                        print(f"  [+] {host}:{port}")
                    sock.close()
                except:
                    pass
        
        self.findings['open_ports'] = open_ports
    
    def _save_results(self):
        """Save findings to disk."""
        report_path = self.output_dir / 'report.json'
        with open(report_path, 'w') as f:
            json.dump(self.findings, f, indent=2)
        
        print(f"[*] Report: {report_path}")
        print(f"[*] Subdomains: {len(self.findings['subdomains'])}")
        print(f"[*] Live hosts: {len(self.findings['live_hosts'])}")
        print(f"[*] Open ports: {len(self.findings['open_ports'])}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 recon.py <target.com>")
        sys.exit(1)
    
    target = sys.argv[1]
    recon = SpecterRecon(target)
    results = recon.run_full_recon()
    
    print(f"\n[+] Complete. Results in: {recon.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
