#!/usr/bin/env python3
"""
SPECTER WEATHER VALIDATOR
Backtests NOAA forecasts against actual outcomes.
Run daily until Ramadan ends to verify edge detection.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import requests

class WeatherValidator:
    def __init__(self):
        self.predictions_file = '/home/ubuntu/.openclaw/workspace/weather_pinnacle/predictions.json'
        self.results_file = '/home/ubuntu/.openclaw/workspace/weather_pinnacle/validation_results.json'

    def log_prediction(self, city: str, noaa_prob: float, event: str, market_price: float):
        """Log daily prediction for later validation."""
        prediction = {
            'timestamp': datetime.now().isoformat(),
            'city': city,
            'noaa_probability': noaa_prob,
            'event': event,
            'market_price': market_price,
            'edge': abs(noaa_prob - market_price),
            'outcome': None,  # To be filled later
            'verified': False
        }
        predictions = self._load_json(self.predictions_file)
        predictions.append(prediction)
        self._save_json(self.predictions_file, predictions)
        return prediction

    def verify_prediction(self, city: str, date: str, actual_outcome: bool):
        """Verify if prediction matched reality."""
        predictions = self._load_json(self.predictions_file)
        for p in predictions:
            if p['city'] == city and p['timestamp'].startswith(date):
                p['outcome'] = actual_outcome
                p['verified'] = True
                # Calculate accuracy
                predicted_yes = p['noaa_probability'] > 0.5
                p['accurate'] = (predicted_yes == actual_outcome)
        self._save_json(self.predictions_file, predictions)

    def calculate_accuracy(self) -> Dict:
        """Calculate overall forecast accuracy."""
        predictions = self._load_json(self.predictions_file)
        verified = [p for p in predictions if p.get('verified')]
        if not verified:
            return {'total': 0, 'accurate': 0, 'accuracy': 0.0}
        accurate = sum(1 for p in verified if p.get('accurate'))
        return {
            'total': len(verified),
            'accurate': accurate,
            'accuracy': accurate / len(verified) if verified else 0.0,
            'high_edge_wins': self._analyze_edge_performance(predictions)
        }

    def _analyze_edge_performance(self, predictions: List[Dict]) -> Dict:
        """Analyze if high-edge predictions perform better."""
        high_edge = [p for p in predictions if p['edge'] > 0.15]
        low_edge = [p for p in predictions if p['edge'] <= 0.15]
        
        # For unverified predictions, estimate accuracy based on NOAA model
        high_edge_acc = sum(1 for p in high_edge if p.get('accurate', False)) / len(high_edge) if high_edge else 0
        low_edge_acc = sum(1 for p in low_edge if p.get('accurate', False)) / len(low_edge) if low_edge else 0
        
        return {
            'high_edge_count': len(high_edge),
            'high_edge_accuracy': high_edge_acc,
            'low_edge_count': len(low_edge),
            'low_edge_accuracy': low_edge_acc
        }

    def run_daily_validation(self):
        """Run validation scan - call this daily."""
        from bot import PinnacleArbitrage
        bot = PinnacleArbitrage(dry_run=True)
        opportunities = bot.find_live_arbitrage()
        logged = []
        for opp in opportunities:
            pred = self.log_prediction(
                opp['city'],
                opp['noaa_probability'],
                opp.get('event_type', 'unknown'),
                opp['market_price']
            )
            logged.append(pred)
        return logged

    def _load_json(self, path: str) -> List:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return []

    def _save_json(self, path: str, data: List):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    validator = WeatherValidator()
    print("=== SPECTER WEATHER VALIDATOR ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("Mode: Pre-Ramadan Validation (No Live Trading)")
    print("-" * 50)

    # Run daily prediction
    predictions = validator.run_daily_validation()
    
    # Show current accuracy
    accuracy = validator.calculate_accuracy()
    
    print(f"\nToday's Predictions Logged: {len(predictions)}")
    print(f"Total Verified Predictions: {accuracy['total']}")
    print(f"Overall Accuracy: {accuracy['accuracy']*100:.1f}%")
    
    if accuracy.get('high_edge_wins'):
        print(f"\nEdge Analysis:")
        he = accuracy['high_edge_wins']
        print(f"  High Edge (>15%): {he['high_edge_count']} pred, {he['high_edge_accuracy']*100:.0f}% acc")
        print(f"  Low Edge (<15%): {he['low_edge_count']} pred, {he['low_edge_accuracy']*100:.0f}% acc")
    
    print("\nNext Steps:")
    print("1. Run this daily until Ramadan ends")
    print("2. Verify outcomes after events complete")
    print("3. If accuracy >70%, deploy $4 capital")
    print("4. If edge strategy works, scale to $20+")
