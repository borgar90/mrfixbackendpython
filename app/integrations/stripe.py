# app/integrations/stripe.py

"""
Module for handling payments via Stripe.
Remember to set environment variables for Stripe API keys.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import stripe
from typing import Dict, Any

STRIPE_SECRET_KEY = os.getenv("STRIPE_SK")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PK")

class StripeClient:
    def __init__(self):
        """
        Initialize Stripe client with API keys.
        """
        if not STRIPE_SECRET_KEY:
            raise ValueError("STRIPE_SK environment variable is required")
        
        stripe.api_key = STRIPE_SECRET_KEY

    def create_payment_intent(self, order_id: int, amount: float, callback_url: str, shipping: Dict[str, Any] = None) -> Dict:
        """
        Create a Stripe Checkout Session for the order (similar to Vipps flow with redirect URL).
        - order_id: unique ID for the order
        - amount: amount in NOK (will be converted to øre for Stripe)
        - callback_url: URL for success/cancel redirects
        - shipping: shipping information for the payment
        """
        try:
            # Extract base URL from callback_url for success/cancel URLs
            import urllib.parse
            parsed_url = urllib.parse.urlparse(callback_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Prepare line items for Stripe Checkout
            line_items = [{
                "price_data": {
                    "currency": "nok",
                    "product_data": {
                        "name": f"Order #{order_id}",
                        "description": f"Payment for order {order_id}"
                    },
                    "unit_amount": int(amount * 100),  # Convert to øre
                },
                "quantity": 1,
            }]

            # Prepare shipping options if provided
            shipping_options = None
            if shipping:
                shipping_options = [{
                    "shipping_rate_data": {
                        "type": "fixed_amount",
                        "fixed_amount": {"amount": 0, "currency": "nok"},
                        "display_name": "Standard shipping",
                    }
                }]

            # Create Checkout Session (provides redirect URL like Vipps)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=f"{base_url}/stripe-success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order_id}",
                cancel_url=f"{base_url}/stripe-cancel?order_id={order_id}",
                metadata={
                    "order_id": str(order_id),
                    "callback_url": callback_url
                },
                shipping_options=shipping_options if shipping_options else None,
                customer_email=shipping.get("email") if shipping else None,
            )

            return {
                "session_id": checkout_session.id,
                "url": checkout_session.url,  # This is the redirect URL (like Vipps)
                "amount": int(amount * 100),
                "currency": "nok",
                "status": "created",
                "order_id": str(order_id)
            }

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create Stripe checkout session: {str(e)}")

    def get_payment_intent_status(self, payment_intent_id: str) -> Dict:
        """
        Get the status of a Stripe PaymentIntent.
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "order_id": payment_intent.metadata.get("order_id")
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get Stripe payment status: {str(e)}")

    def confirm_payment_intent(self, payment_intent_id: str) -> Dict:
        """
        Confirm a Stripe PaymentIntent (usually done client-side, but useful for testing).
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to confirm Stripe payment: {str(e)}")
