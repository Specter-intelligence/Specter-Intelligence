"""
Polymarket CLOB API Integration
Live market data for weather arbitrage.
"""

import requests
import json
from datetime import datetime
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class PolymarketCLOB:
    """
    Polymarket Central Limit Order Book client.
    Uses public API - no auth required for market data.
    """
    
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.markets_cache = {}
        
    def get_active_markets(self, tag: str = "weather") -> List[Dict]:
        """Fetch active markets with weather tag."""
        url = f"{self.BASE_URL}/markets"
        params = {"active": "true", "tag": tag}
        
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            markets = resp.json()
            
            # Filter for weather-related
            weather_keywords = ['rain', 'snow', 'storm', 'temperature', 'weather', 'forecast']
            filtered = [
                m for m in markets 
                if any(kw in m.get('question', '').lower() for kw in weather_keywords)
            ]
            
            logger.info(f"Found {len(filtered)} weather markets")
            return filtered
            
        except Exception as e:
            logger.error(f"CLOB fetch failed: {e}")
            return []
    
    def get_market_data(self, market_id: str) -> Optional[Dict]:
        """Get specific market order book."""
        url = f"{self.BASE_URL}/markets/{market_id}"
        
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            return {
                'market_id': market_id,
                'question': data.get('question', ''),
                'yes_price': float(data.get('best_bid', {}).get('price', 0)),
                'no_price': 1.0 - float(data.get('best_ask', {}).get('price', 1.0)),
                'volume': float(data.get('volume', 0)),
                'end_date': datetime.fromisoformat(data.get('end_date_iso', datetime.now().isoformat())),
                'active': data.get('active', False)
            }
            
        except Exception as e:
            logger.error(f"Market {market_id} fetch failed: {e}")
            return None
    
    def match_weather_markets(self, city: str, noaa_forecast: float) -> List[Dict]:
        """Find markets matching NOAA forecast."""
        markets = self.get_active_markets()
        matches = []
        
        city_patterns = {
            'san_jose': ['san jose', 'bay area'],
            'san_diego': ['san diego'],
            'houston': ['houston', 'texas'],
            'phoenix': ['phoenix', 'arizona'],
            'new_york': ['new york', 'nyc'],
            'los_angeles': ['los angeles', 'la'],
            'chicago': ['chicago'],
            'philadelphia': ['philadelphia'],
            'san_antonio': ['san antonio'],
            'dallas': ['dallas']
        }
        
        patterns = city_patterns.get(city.lower().replace(' ', '_'), [city.lower()])
        
        for market in markets:
            question = market.get('question', '').lower()
            
            if any(p in question for p in patterns):
                market_data = self.get_market_data(market.get('id'))
                if market_data:
                    # Calculate edge
                    edge = abs(noaa_forecast - market_data['yes_price'])
                    if edge > 0.15:  # 15% minimum
                        market_data['edge'] = edge
                        market_data['city'] = city
                        market_data['noaa_prob'] = noaa_forecast
                        matches.append(market_data)
        
        return matches
    
    def get_order_book(self, token_id: str) -> Dict:
        """Get live order book for price execution."""
        url = f"{self.BASE_URL}/book"
        params = {"token_id": token_id}
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Order book fetch failed: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    clob = PolymarketCLOB()
    markets = clob.get_active_markets()
    print(f"Found {len(markets)} weather markets")
    for m in markets[:3]:
        print(f"  - {m.get('question', 'N/A')[:60]}...")
