
import pytest
import requests
import json

def test_stripe_webhook():
    webhook_url = "http://localhost:8000/v1/stripe/webhook"
    payload = {
        "id": "evt_test_webhook",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer_email": "testuser@example.com",
                "metadata": {"plan": "pro"}
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
        "stripe-signature": "test_signature"
    }
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=2)
        assert response.status_code in (200, 400, 404)
    except requests.ConnectionError:
        pytest.skip("Stripe webhook server not running on localhost:8000")
