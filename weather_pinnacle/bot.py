#!/usr/bin/env python3
"""
SPECTER WEATHER PINNACLE v2 - LIVE
Production-grade weather arbitrage with Polymarket CLOB integration.
"""
import requests
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherForecast:
    city: str
    probability: float
    event_type: str
    timestamp: datetime

class PolymarketCLOB:
    """Polymarket Central Limit Order Book client."""
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self._markets_cache = None
        self._cache_time = None
    
    def get_weather_markets(self) -> List[Dict]:
        """Fetch live weather markets from Polymarket."""
        # Check cache (5 min TTL)
        if self._markets_cache and self._cache_time:
            if (datetime.now() - self._cache_time).seconds < 300:
                return self._markets_cache
        
        url = f"{self.BASE_URL}/markets"
        params = {"active": "true", "closed": "false"}
        
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            if 'data' not in data:
                logger.error("Invalid CLOB response structure")
                return []
            
            markets = data['data']
            
            # Filter weather markets
            weather_keywords = ['rain', 'snow', 'storm', 'temperature', 'weather', 'forecast', 'precipitation']
            cities = ['new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 
                      'san antonio', 'san diego', 'dallas', 'san jose', 'miami', 'boston', 
                      'seattle', 'denver', 'atlanta']
            
            weather_markets = []
            for m in markets:
                question = m.get('question', '').lower()
                
                # Weather keyword match
                is_weather = any(kw in question for kw in weather_keywords)
                # City match
                has_city = any(city in question for city in cities)
                
                if is_weather and has_city:
                    tokens = m.get('tokens', [])
                    if len(tokens) >= 2:
                        market_data = {
                            'market_id': m.get('condition_id', ''),
                            'question': m.get('question', ''),
                            'yes_price': tokens[0].get('price', 0),
                            'no_price': tokens[1].get('price', 0),
                            'volume': m.get('volume', 0),
                            'end_date': m.get('end_date_iso', ''),
                            'city': self._extract_city(question)
                        }
                        weather_markets.append(market_data)
            
            self._markets_cache = weather_markets
            self._cache_time = datetime.now()
            logger.info(f"Found {len(weather_markets)} live weather markets on Polymarket")
            return weather_markets
            
        except Exception as e:
            logger.error(f"CLOB fetch failed: {e}")
            return []
    
    def _extract_city(self, question: str) -> str:
        """Extract city name from market question."""
        cities = {
            'new york': 'new_york', 'los angeles': 'los_angeles', 'chicago': 'chicago',
            'houston': 'houston', 'phoenix': 'phoenix', 'philadelphia': 'philadelphia',
            'san antonio': 'san_antonio', 'san diego': 'san_diego', 'dallas': 'dallas',
            'san jose': 'san_jose', 'miami': 'miami', 'boston': 'boston',
            'seattle': 'seattle', 'denver': 'denver', 'atlanta': 'atlanta'
        }
        q = question.lower()
        for city_name, city_key in cities.items():
            if city_name in q:
                return city_key
        return 'unknown'

class PinnacleArbitrage:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.capital = 4.0 if not dry_run else 0.0
        self.min_edge = 0.15
        self.logger = logger
        self.clob = PolymarketCLOB()
    
    def fetch_noaa_forecast(self, city: str) -> Optional[WeatherForecast]:
        """Fetch NOAA forecast for city."""
        coords = {
            'new_york': '40.7128,-74.0060', 'los_angeles': '34.0522,-118.2437',
            'chicago': '41.8781,-87.6298', 'houston': '29.7604,-95.3698',
            'phoenix': '33.4484,-112.0740', 'philadelphia': '39.9526,-75.1652',
            'san_antonio': '29.4241,-98.4936', 'san_diego': '32.7157,-117.1611',
            'dallas': '32.7767,-96.7970', 'san_jose': '37.3382,-121.8863',
            'miami': '25.7617,-80.1918', 'boston': '42.3601,-71.0589',
            'seattle': '47.6062,-122.3321', 'denver': '39.7392,-104.9903',
            'atlanta': '33.7490,-84.3880'
        }
        
        point_url = f"https://api.weather.gov/points/{coords.get(city, '40.7128,-74.0060')}"
        
        try:
            resp = requests.get(point_url, headers={'Accept': 'application/json'}, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            forecast_url = data['properties']['forecast']
            forecast_resp = requests.get(forecast_url, timeout=10)
            if forecast_resp.status_code != 200:
                return None
            
            periods = forecast_resp.json()['properties']['periods']
            for period in periods[:3]:
                prob_data = period.get('probabilityOfPrecipitation', {})
                prob = prob_data.get('value', 0) if isinstance(prob_data, dict) else 0
                if prob is not None and prob > 0:
                    return WeatherForecast(
                        city=city,
                        probability=prob / 100.0,
                        event_type=period['shortForecast'],
                        timestamp=datetime.now()
                    )
            return None
        except Exception as e:
            self.logger.error(f"NOAA failed for {city}: {e}")
            return None
    
    def kelly_criterion(self, win_prob: float, win_odds: float) -> float:
        """Half-Kelly position sizing."""
        if win_prob <= 0 or win_odds <= 0:
            return 0.0
        q = 1.0 - win_prob
        kelly = (win_odds * win_prob - q) / win_odds
        return max(0.0, kelly * 0.5)  # Conservative half-Kelly
    
    def find_live_arbitrage(self) -> List[Dict]:
        """Find live arbitrage opportunities vs Polymarket."""
        opportunities = []
        markets = self.clob.get_weather_markets()
        
        self.logger.info(f"Scanning {len(markets)} live markets for edges")
        
        for market in markets:
            city = market.get('city')
            if city == 'unknown':
                continue
            
            # Get NOAA forecast
            forecast = self.fetch_noaa_forecast(city)
            if not forecast:
                continue
            
            # Calculate edge
            market_price = market['yes_price']
            edge = abs(forecast.probability - market_price)
            
            if edge < self.min_edge:
                continue
            
            # Kelly sizing
            win_odds = 1.0 / market_price if market_price > 0 else 0
            kelly = self.kelly_criterion(forecast.probability, win_odds)
            position = min(kelly * self.capital, self.capital * 0.25)
            
            # Determine recommendation
            if forecast.probability > market_price:
                recommendation = "BUY YES (NOAA predicts higher than market)"
                expected_roi = position * (forecast.probability * win_odds - 1)
            else:
                recommendation = "BUY NO (NOAA predicts lower than market)"
                expected_roi = position * ((1 - forecast.probability) * (1/market['no_price']) - 1)
            
            opp = {
                'city': city,
                'question': market['question'],
                'noaa_probability': forecast.probability,
                'event_type': forecast.event_type,
                'market_price': market_price,
                'edge': edge,
                'position_size': position,
                'expected_roi': expected_roi,
                'recommendation': recommendation,
                'volume': market.get('volume', 0),
                'end_date': market.get('end_date', '')
            }
            opportunities.append(opp)
        
        return opportunities

if __name__ == "__main__":
    bot = PinnacleArbitrage(dry_run=True)
    ops = bot.find_live_arbitrage()
    print(f"Found {len(ops)} opportunities")
    for op in ops:
        print(f"  {op['city']}: {op['edge']*100:.1f}% edge")
