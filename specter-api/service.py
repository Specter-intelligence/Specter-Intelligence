#!/usr/bin/env python3
"""Specter Intelligence API - x402 powered microservices"""
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)
REQUIRED_PAYMENT = 0.001  # RTC micropricing

def require_payment(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payment = request.headers.get('X-402-Payment')
        if not payment:
            return jsonify({"error": "Payment required", "x402": {"amount": REQUIRED_PAYMENT, "currency": "RTC"}}), 402
        return f(*args, **kwargs)
    return decorated

@app.route('/health')
def health():
    return jsonify({"status": "specter-intelligence", "rate": f"{REQUIRED_PAYMENT} RTC", "services": ["webhook", "scrape", "intel"]})

@app.route('/webhook/send', methods=['POST'])
@require_payment
def webhook():
    return jsonify({"status": "sent", "cost": REQUIRED_PAYMENT})

@app.route('/intel/crypto', methods=['GET'])
@require_payment
def intel():
    return jsonify({"alpha": "4claw_scan", "cost": REQUIRED_PAYMENT})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8402)