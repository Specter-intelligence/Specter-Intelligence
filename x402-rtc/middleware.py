"""
x402 RTC Payment Middleware for Flask/FastAPI.
Implements HTTP 402 Payment Required with RustChain RTC payments.
"""
from flask import request, jsonify, make_response
import functools
import time
import uuid

# Default RustChain node URL (live network)
DEFAULT_NODE_URL = "https://50.28.86.131"
PAYMENT_ENDPOINT = f"{DEFAULT_NODE_URL}/wallet/transfer/signed"

class RTC402Middleware:
    """Middleware to gate endpoints behind RTC payments."""
    
    def __init__(self, app=None, node_url=None, default_amount=0.001):
        self.node_url = node_url or DEFAULT_NODE_URL
        self.default_amount = default_amount
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.extensions['rtc402'] = self
    
    def require_payment(self, amount=None, currency="RTC", address=None):
        """Decorator that returns 402 Payment Required with RTC headers."""
        def decorator(f):
            @functools.wraps(f)
            def wrapped(*args, **kwargs):
                # Check for payment proof in request headers
                payment_proof = request.headers.get('X-Payment-Proof')
                if payment_proof and self.verify_payment(payment_proof):
                    # Payment verified, proceed
                    return f(*args, **kwargs)
                
                # No valid proof → 402
                resp = make_response(jsonify({
                    "error": "Payment Required",
                    "message": "This endpoint requires RTC payment."
                }), 402)
                
                # x402 headers
                resp.headers['X-Payment-Amount'] = str(amount or self.default_amount)
                resp.headers['X-Payment-Currency'] = currency
                if address:
                    resp.headers['X-Payment-Address'] = address
                else:
                    # Default to node's payment address (should be configured)
                    resp.headers['X-Payment-Address'] = "RTCa1b2c3d4..."  # placeholder
                resp.headers['X-Payment-Network'] = "rustchain"
                resp.headers['X-Payment-Endpoint'] = PAYMENT_ENDPOINT
                resp.headers['X-Payment-Id'] = str(uuid.uuid4())
                resp.headers['X-Payment-Expires'] = str(int(time.time()) + 300)  # 5min
                
                return resp
            return wrapped
        return decorator
    
    def verify_payment(self, payment_proof: str) -> bool:
        """Verify a payment proof (signature, transaction hash, etc.)."""
        # TODO: implement verification with RustChain node
        # For now, accept any non-empty proof (demo)
        return bool(payment_proof and payment_proof.strip())


# Flask extension instance
rtc402 = RTC402Middleware()

# Convenience decorator
def require_rtc_payment(amount=None, currency="RTC", address=None):
    """Standalone decorator for Flask routes."""
    return rtc402.require_payment(amount, currency, address)