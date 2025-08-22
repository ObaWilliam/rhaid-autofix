import requests
import json

# Simulate Stripe webhook payload for checkout.session.completed
webhook_url = "http://localhost:8000/v1/stripe/webhook"

# Example test payload (normally sent by Stripe)
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
    "stripe-signature": "test_signature"  # Not validated in test mode
}

response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
print("Status:", response.status_code)
print("Response:", response.json())
