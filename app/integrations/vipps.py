# app/integrations/vipps.py

"""
Modul for å håndtere betaling via Vipps.
Husk å fylle ut miljøvariabler i .env og oppdatere URL-er om du går til produksjon.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import requests
from typing import Dict, Any

VIPPS_CLIENT_ID = os.getenv("VIPPS_CLIENT_ID")
VIPPS_CLIENT_SECRET = os.getenv("VIPPS_CLIENT_SECRET")
VIPPS_SANDBOX_URL = os.getenv("VIPPS_SANDBOX_URL", "https://apitest.vipps.no")  # e.g., https://apitest.vipps.no
VIPPS_PRODUCTION_URL = os.getenv("VIPPS_PRODUCTION_URL", "https://api.vipps.no")  # e.g., https://api.vipps.no
VIPPS_SANDBOX_PAYMENT_URL = os.getenv("VIPPS_SANDBOX_PAYMENT_URL", "https://pay-mt.vipps.no")
VIPPS_PRODUCTION_PAYMENT_URL = os.getenv("VIPPS_PRODUCTION_PAYMENT_URL", "https://pay.vipps.no")
VIPPS_APIM_SUBSCRIPTION_KEY = os.getenv("VIPPS_APIM_SUBSCRIPTION_KEY")
MERCHANT_SERIAL_NUMBER = os.getenv("VIPPS_MERCHANT_SERIAL_NUMBER")
VIPPS_SYSTEM_NAME = os.getenv("VIPPS_SYSTEM_NAME", "mrfixweb")
VIPPS_SYSTEM_VERSION = os.getenv("VIPPS_SYSTEM_VERSION", "1.0.0")
VIPPS_SYSTEM_PLUGIN_NAME = os.getenv("VIPPS_SYSTEM_PLUGIN_NAME", "mrfixweb-plugin")
VIPPS_SYSTEM_PLUGIN_VERSION = os.getenv("VIPPS_SYSTEM_PLUGIN_VERSION", "1.0.0")

class VippsClient:
    def __init__(self, sandbox: bool = True):
        """
        Initialiser klient med sandbox eller produksjons-URL.
        """
        # Separate base URLs for auth and payment
        if sandbox:
            self.auth_base_url = VIPPS_SANDBOX_URL
            self.payment_base_url = VIPPS_SANDBOX_PAYMENT_URL
            print(f"{VIPPS_CLIENT_SECRET} VippsClient initialized in sandbox mode")
        else:
            self.auth_base_url = VIPPS_PRODUCTION_URL
            self.payment_base_url = VIPPS_PRODUCTION_PAYMENT_URL
        
        self.access_token = None
        # defer authentication until needed

    def _authenticate(self):
        """
        Autentiser mot Vipps for å hente tilgangstoken.
        """
        print("Starting authentication with Vipps...")
        # Ensure credentials configured
        if not VIPPS_CLIENT_ID or not VIPPS_CLIENT_SECRET or not VIPPS_APIM_SUBSCRIPTION_KEY:
            raise Exception("Missing Vipps configuration in environment")
        
        auth_url = f"{self.auth_base_url}/accesstoken/get"
        print(f"Auth URL: {auth_url}")
        
        # Use Vipps specific header authentication method
        headers = {
            "Content-Type": "application/json",
            "client_id": VIPPS_CLIENT_ID,
            "client_secret": VIPPS_CLIENT_SECRET,
            "Ocp-Apim-Subscription-Key": VIPPS_APIM_SUBSCRIPTION_KEY,
            "Merchant-Serial-Number": MERCHANT_SERIAL_NUMBER
        }
        
        # Empty data as per Vipps documentation
        data = ""
        print(f"Auth data: {data}")
        print(f"Auth headers: {headers}")
        
        resp = requests.post(auth_url, data=data, headers=headers)
        print(f"Auth response status: {resp.status_code}")
        print(f"Auth response body: {resp.text}")
        
        if resp.status_code == 200:
            response_data = resp.json()
            # Token key may be 'accessToken' or 'access_token'
            self.access_token = response_data.get("accessToken") or response_data.get("access_token")
            print(f"Access token obtained: {self.access_token}")
        else:
            raise Exception(f"Failed to authenticate with Vipps: {resp.text}")

    def create_payment(
        self,
        order_id: int,
        amount: float,
        callback_url: str,
        shipping: Dict[str, Any] = None,
        receipt: Dict[str, Any] = None,
        idempotency_key: str = None,
        extras: Dict[str, Any] = None
    ) -> Dict:
        """
        Opprett en betalingsforespørsel i Vipps.
        Pass in `extras` dict to merge any additional fields (e.g., industryData, profile, metadata, expiresAt, shipping options, qrFormat, minimumUserAge).
        """
        print("Starting payment creation...")
        print(f"Order ID: {order_id}, Amount: {amount}, Callback URL: {callback_url}")
        print(f"Shipping: {shipping}, Receipt: {receipt}, Extras: {extras}")
        # Ensure authenticated
        if not self.access_token:
            print("No access token found, authenticating...")
            self._authenticate()

        # Default idempotency key
        if not idempotency_key:
            import uuid
            idempotency_key = str(uuid.uuid4())
        print(f"Idempotency Key: {idempotency_key}")

        # Use ePayment v1 endpoint on API host (apitest.vipps.no)
        url = f"{self.auth_base_url}/epayment/v1/payments"
        print(f"Payment URL: {url}")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": VIPPS_APIM_SUBSCRIPTION_KEY,
            "Merchant-Serial-Number": MERCHANT_SERIAL_NUMBER,
            "Vipps-System-Name": VIPPS_SYSTEM_NAME,
            "Vipps-System-Version": VIPPS_SYSTEM_VERSION,
            "Vipps-System-Plugin-Name": VIPPS_SYSTEM_PLUGIN_NAME,
            "Vipps-System-Plugin-Version": VIPPS_SYSTEM_PLUGIN_VERSION,
            "Idempotency-Key": idempotency_key
        }
        print(f"Payment headers: {headers}")        # Build request body according to ePayment API
        # Ensure reference is 8-64 characters and alphanumeric with dashes
        reference = f"mrfixweb-order-{order_id}"
        if len(reference) < 8:
            reference = f"mrfixweb-order-{order_id:08d}"  # Pad with zeros if needed
        elif len(reference) > 64:
            reference = reference[:64]  # Truncate if too long
        
        # Clean phone number - remove + and spaces, keep only digits
        phone_number = "4712345678"  # Default test number
        if shipping and shipping.get("phone"):
            clean_phone = ''.join(filter(str.isdigit, shipping.get("phone")))
            if 10 <= len(clean_phone) <= 15:
                phone_number = clean_phone
        
        body = {
            "amount": {"currency": "NOK", "value": int(amount * 100)},
            "paymentMethod": {"type": "WALLET"},
            "customer": {"phoneNumber": phone_number},
            "reference": reference,
            "userFlow": "WEB_REDIRECT",
            "returnUrl": callback_url,
            "paymentDescription": f"Payment for order {order_id}"
        }
        print(f"Payment body before extras: {body}")
        # Include receipt if provided
        if receipt:
            body["receipt"] = receipt
        # Merge any extras
        if extras:
            for key, value in extras.items():
                body[key] = value
        print(f"Final payment body: {body}")

        resp = requests.post(url, json=body, headers=headers)
        print(f"Payment response status: {resp.status_code}")
        print(f"Payment response body: {resp.text}")
        if resp.status_code in (200, 201):
            return resp.json()
        else:
            raise Exception(f"Failed to create Vipps payment: {resp.text}")

    def get_payment_status(self, payment_id: str) -> Dict:
        """
        Hent betalingsstatus for payment_id.
        """
        if not self.access_token:
            self._authenticate()
        url = f"{self.payment_base_url}/ecomm/v2/payments/{payment_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Ocp-Apim-Subscription-Key": VIPPS_APIM_SUBSCRIPTION_KEY
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Failed to get Vipps payment status: {resp.text}")
