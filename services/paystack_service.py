import requests
from flask import current_app

def initialize_transaction(email, amount, reference, currency="NGN", metadata=None):
    url = (f"{current_app.config['PAYSTACK_BASE_URL']}/transaction/initialize")

    headers = {
        "Authorization": (f"Bearer {current_app.config['PAYSTACK_SECRET_KEY']}"),
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": str(amount),
        "currency": currency,
        "reference": reference,
        "metadata": metadata or {}
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    response.raise_for_status()

    return response.json()