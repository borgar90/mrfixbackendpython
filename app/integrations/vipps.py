# app/integrations/vipps.py

"""
Modul for å håndtere betaling via Vipps.
Husk å fylle ut miljøvariabler i .env og oppdatere URL-er om du går til produksjon.
"""

import os
import requests
from typing import Dict

VIPPS_CLIENT_ID = os.getenv("VIPPS_CLIENT_ID")
VIPPS_CLIENT_SECRET = os.getenv("VIPPS_CLIENT_SECRET")
VIPPS_SANDBOX_URL = os.getenv("VIPPS_SANDBOX_URL")
VIPPS_PRODUCTION_URL = os.getenv("VIPPS_PRODUCTION_URL")

class VippsClient:
    def __init__(self, sandbox: bool = True):
        """
        Initialiser klient med sandbox eller produksjons-URL.
        """
        if sandbox:
            self.base_url = VIPPS_SANDBOX_URL
        else:
            self.base_url = VIPPS_PRODUCTION_URL
        self.access_token = None
        self._authenticate()

    def _authenticate(self):
        """
        Autentiser mot Vipps for å hente tilgangstoken.
        """
        auth_url = f"{self.base_url}/accesstoken/get"
        payload = {
            "client_id": VIPPS_CLIENT_ID,
            "client_secret": VIPPS_CLIENT_SECRET
        }
        headers = {
            "Content-Type": "application/json"
        }
        resp = requests.post(auth_url, json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            self.access_token = data.get("access_token")
        else:
            raise Exception(f"Failed to authenticate with Vipps: {resp.text}")

    def create_payment(self, order_id: int, amount: float, callback_url: str) -> Dict:
        """
        Opprett en betalingsforespørsel i Vipps.
        - order_id: unik ID for ordren
        - amount: beløp i øre (NOK * 100)
        - callback_url: URL som Vipps kaller når betaling er godkjent/avbrutt
        """
        if not self.access_token:
            self._authenticate()

        url = f"{self.base_url}/ecomm/v2/payments"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "merchantInfo": {
                "merchantSerialNumber": "YOUR_MERCHANT_SERIAL_NUMBER",
                "callbackPrefix": callback_url,
                "fallBack": callback_url,
                "isApp": False,
                "merchantName": "Din Webshop AS",
                "paymentType": "eComm Express Payment"
            },
            "customerInfo": {
                "mobileNumber": "47xxxxxxxx",
                "email": "customer@example.com"
            },
            "transaction": {
                "orderId": str(order_id),
                "amount": int(amount * 100),  # Vipps forventer øre
                "currency": "NOK",
                "transactionText": f"Payment for order {order_id}"
            }
        }
        resp = requests.post(url, json=body, headers=headers)
        if resp.status_code == 200 or resp.status_code == 201:
            return resp.json()
        else:
            raise Exception(f"Failed to create Vipps payment: {resp.text}")

    def get_payment_status(self, payment_id: str) -> Dict:
        """
        Hent betalingsstatus for payment_id.
        """
        if not self.access_token:
            self._authenticate()
        url = f"{self.base_url}/ecomm/v2/payments/{payment_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Failed to get Vipps payment status: {resp.text}")
