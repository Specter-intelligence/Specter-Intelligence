import sys
from scrapling.fetchers import Fetcher
import re
import json
import datetime

def scrape_dropsearn():
    print("Scraping Dropsearn...")
    try:
        page = Fetcher.get('https://dropsearn.com/')
        # Basic parsing using regex if CSS fails
        text = page.text
        # Look for project names and descriptions in common tags
        # <a href="/projects/xxx/">Project Name</a>
        projects = re.findall(r'<a[^>]+href="/projects/[^/]+/"[^>]*>(.*?)</a>', text)
        return list(set(projects))[:10]
    except Exception as e:
        return [f"Error: {str(e)}"]

def scrape_immunefi():
    print("Scraping Immunefi...")
    try:
        # Try home page first for status
        page = Fetcher.get('https://immunefi.com/')
        text = page.text
        # Look for reward amounts
        rewards = re.findall(r'\$[\d,]+[^\d\s]*(?:million|M|K)?', text, re.IGNORECASE)
        return sorted(list(set(rewards)), key=len, reverse=True)[:10]
    except Exception as e:
        return [f"Error: {str(e)}"]

def main():
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "dropsearn": scrape_dropsearn(),
        "immunefi": scrape_immunefi(),
    }
    
    with open('alpha_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\nAlpha Report Saved to alpha_report.json")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
