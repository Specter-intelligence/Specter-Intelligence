#!/usr/bin/env python3
"""GitHub-based alpha scanner — no Brave API needed"""
from scrapling.fetchers import Fetcher
import json
from datetime import datetime

Fetcher.configure(adaptive=True)

def search_github(query):
    """Search GitHub for repositories"""
    url = f'https://github.com/search?q={query}&type=repositories&s=updated&o=desc'
    page = Fetcher.get(url)
    
    links = page.css('a[href^="/"]')
    repos = []
    for link in links:
        href = link.attr('href')
        text = link.text.strip() if link.text else ''
        if href and '/' in href and len(href.split('/')) == 2 and text and len(text) > 2:
            if text not in ['Explore', 'Pricing', 'Docs', 'Sign in', 'Sign up', 'Trending']:
                repos.append((text, href))
    
    return list(dict.fromkeys(repos))[:10

print(f"=== Alpha Scan — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} ===")

print("\n[TESTNET / INCENTIVE REPOS]")
testnets = search_github('testnet+incentive')
for name, url in testnets[:5]:
    print(f"  github.com{url} — {name}")

print("\n[AIRDROP / REWARDS REPOS]")
airdrops = search_github('airdrop+rewards')
for name, url in airdrops[:5]:
    print(f"  github.com{url} — {name}")

print("\n[SMART CONTRACT / DEPLOYMENT]")
contracts = search_github('smart+contract+deploy+ethereum')
for name, url in contracts[:5]:
    print(f"  github.com{url} — {name}")
