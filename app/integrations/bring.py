# app/integrations/bring.py

"""
Modul for grunnleggende Bring-integrasjon. 
Eksempel: opprett fraktbestilling.
Husk å fylle inn BRING_API_KEY i .env.
"""

import os
import requests
from typing import Dict

BRING_API_KEY = os.getenv("BRING_API_KEY")
BRING_API_URL = os.getenv("BRING_API_URL", "https://api.bring.com")

class BringClient:
    def __init__(self):
        """
        Initialiser klient. Bruk API-nøkkelen som query-parametrer eller header avhengig av Bring-API.
        """
        self.api_key = BRING_API_KEY
        self.base_url = BRING_API_URL

    def create_shipment(self, order_id: int, recipient: Dict, items: Dict) -> Dict:
        """
        Opprett en forsendelsesordre i Bring.
        - order_id: unik ID for ordren
        - recipient: informasjon om mottaker (adresse, navn, postnummer, etc.)
        - items: informasjon om antall kolli, vekt, dimensjoner, etc.
        """
        url = f"{self.base_url}/shippingGuide/shipments"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        body = {
            "orderId": str(order_id),
            "recipient": recipient,
            "items": items
        }
        resp = requests.post(url, json=body, headers=headers)
        if resp.status_code in (200, 201):
            return resp.json()
        else:
            raise Exception(f"Failed to create Bring shipment: {resp.text}")

    def get_shipment_status(self, shipment_id: str) -> Dict:
        """
        Hent status på en forsendelse fra Bring.
        """
        url = f"{self.base_url}/shippingGuide/shipments/{shipment_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Failed to fetch Bring shipment status: {resp.text}")
