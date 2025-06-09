#!/usr/bin/env python3
"""
Script to manually trigger Stripe webhook events for testing.
This simulates what Stripe would send when a payment is completed.
"""

import requests
import json

# Simulate a Stripe webhook payload for a completed checkout session
def simulate_stripe_webhook(order_id: int, base_url: str = "http://localhost:8000"):
    webhook_payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": f"cs_test_fake_{order_id}",
                "metadata": {
                    "order_id": str(order_id)
                },
                "payment_status": "paid"
            }
        }
    }
    
    url = f"{base_url}/payment/stripe/webhook"
    headers = {
        "Content-Type": "application/json",
        "stripe-signature": "fake_signature_for_testing"
    }
    
    try:
        response = requests.post(url, json=webhook_payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ Successfully updated order {order_id} to paid status")
            return True
        else:
            print(f"❌ Failed to update order {order_id}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending webhook for order {order_id}: {e}")
        return False

if __name__ == "__main__":
    # List of order IDs that should be marked as paid
    # Update this list with the order IDs that you know were successfully paid through Stripe
    orders_to_mark_paid = [17, 18, 19, 20, 22]  # Add/remove order IDs as needed (21 is already paid)
    
    print("Simulating Stripe webhook events for completed payments...")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print()
    
    success_count = 0
    for order_id in orders_to_mark_paid:
        print(f"Processing order {order_id}...")
        if simulate_stripe_webhook(order_id):
            success_count += 1
    
    print(f"\nCompleted: {success_count}/{len(orders_to_mark_paid)} orders updated successfully")
