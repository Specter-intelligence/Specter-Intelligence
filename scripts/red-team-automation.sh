#!/bin/bash
# Red Team Automation Script
# Integrates existing tools with OpenClaw automation

set -e

TOOL="$1"
TARGET="$2"
OUTPUT_DIR="/home/ubuntu/.openclaw/workspace/scans"
mkdir -p "$OUTPUT_DIR"

timestamp() {
  date '+%Y-%m-%d_%H-%M-%S'
}

case "$TOOL" in
  "nmap-quick")
    # Quick port scan
    echo "[$(timestamp)] Starting nmap quick scan of $TARGET"
    OUTPUT="$OUTPUT_DIR/nmap_quick_$(echo $TARGET | tr '/' '_')_$(timestamp).xml"
    nmap -T4 -F "$TARGET" -oX "$OUTPUT"
    echo "Results: $OUTPUT"
    ;;
    
  "nmap-full")
    # Full port scan with service detection
    echo "[$(timestamp)] Starting nmap full scan of $TARGET"
    OUTPUT="$OUTPUT_DIR/nmap_full_$(echo $TARGET | tr '/' '_')_$(timestamp).xml"
    nmap -T4 -A -p- "$TARGET" -oX "$OUTPUT"
    echo "Results: $OUTPUT"
    ;;
    
  "masscan-fast")
    # Ultra-fast port scan
    echo "[$(timestamp)] Starting masscan of $TARGET"
    OUTPUT="$OUTPUT_DIR/masscan_$(echo $TARGET | tr '/' '_')_$(timestamp).txt"
    masscan -p1-65535 "$TARGET" --rate=1000 -oL "$OUTPUT"
    echo "Results: $OUTPUT"
    ;;
    
  "nikto-web")
    # Web server scan
    echo "[$(timestamp)] Starting nikto scan of $TARGET"
    OUTPUT="$OUTPUT_DIR/nikto_$(echo $TARGET | tr '/' '_')_$(timestamp).txt"
    nikto -h "$TARGET" -output "$OUTPUT"
    echo "Results: $OUTPUT"
    ;;
    
  "sqlmap-test")
    # Basic SQL injection test
    echo "[$(timestamp)] Starting sqlmap test of $TARGET"
    OUTPUT="$OUTPUT_DIR/sqlmap_$(echo $TARGET | tr '/' '_')_$(timestamp).txt"
    sqlmap -u "$TARGET" --batch --level=1 --risk=1 > "$OUTPUT"
    echo "Results: $OUTPUT"
    ;;
    
  "recon-summary")
    # Run multiple recon tools
    echo "[$(timestamp)] Starting comprehensive recon of $TARGET"
    SUMMARY="$OUTPUT_DIR/recon_summary_$(echo $TARGET | tr '/' '_')_$(timestamp).md"
    
    echo "# Recon Summary for $TARGET" > "$SUMMARY"
    echo "## Scan started: $(timestamp)" >> "$SUMMARY"
    
    # Quick nmap
    echo "### 1. Quick Port Scan" >> "$SUMMARY"
    nmap -T4 -F "$TARGET" | tail -20 >> "$SUMMARY"
    
    # Nikto if HTTP
    echo "### 2. Web Server Scan" >> "$SUMMARY"
    nikto -h "$TARGET" -Format txt | tail -30 >> "$SUMMARY" 2>/dev/null || echo "Not a web server or error" >> "$SUMMARY"
    
    echo "## Scan completed: $(timestamp)" >> "$SUMMARY"
    echo "Full results in: $OUTPUT_DIR"
    ;;
    
  "list-tools")
    echo "Available red team tools:"
    echo "1. nmap-quick TARGET - Quick port scan"
    echo "2. nmap-full TARGET - Full port scan with services"
    echo "3. masscan-fast TARGET - Ultra-fast port scan"
    echo "4. nikto-web TARGET - Web server vulnerability scan"
    echo "5. sqlmap-test URL - SQL injection test"
    echo "6. recon-summary TARGET - Comprehensive recon report"
    ;;
    
  *)
    echo "Usage: $0 {nmap-quick|nmap-full|masscan-fast|nikto-web|sqlmap-test|recon-summary|list-tools} TARGET"
    echo "Example: $0 nmap-quick 192.168.1.1"
    exit 1
    ;;
esac