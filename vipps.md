# Vipps Integration

This document explains how the FastAPI backend integrates with Vipps for payment processing, and how to consume the endpoints from your front-end application.

---

## Configuration

Before using Vipps in sandbox or production, set the following environment variables (e.g. in `.env`):

```bash
VIPPS_CLIENT_ID=your-client-id
VIPPS_CLIENT_SECRET=your-client-secret
VIPPS_SANDBOX_URL=https://apitest.vipps.no
VIPPS_PRODUCTION_URL=https://api.vipps.no
```

FastAPI will load these at startup and authenticate with Vipps automatically.

---

## Backend Endpoints

### Initiate Vipps Payment

**POST** `/payment/vipps/initiate`
- Auth: Bearer JWT (customer)
- Request body (JSON):
  ```json
  {
    "order_id": 123,
    "callback_url": "https://your-frontend.com/vipps-result",
    "shipping": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "address": "123 Main St",
      "city": "Oslo",
      "postal_code": "0123",
      "country": "Norway",
      "phone": "+4712345678"
    }
  }
  ```
- Response (JSON):
  ```json
  {
    "data": {
      "orderId": "123",
      "paymentId": "abcde12345",
      "status": "CREATED",
      "url": "https://apitest.vipps.no/payments/...