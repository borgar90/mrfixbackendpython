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

### Initiate Payment

**POST** `/orders/{order_id}/pay`
- Auth: Bearer JWT (customer)
- Request body (JSON):
  ```json
  {
    "callback_url": "https://your-frontend.com/vipps-result"
  }
  ```
- Response (JSON):
  ```json
  {
    "data": {
      // Raw Vipps API response, for example:
      "orderId": "123",
      "paymentId": "abcde12345",
      "status": "CREATED",
      "url": "https://apitest.vipps.no/payments/...",