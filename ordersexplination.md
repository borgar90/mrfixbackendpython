# Orders Endpoint Guide

This document explains how to use the Webshop API's order endpoints, including examples for each operation.

---

## Authentication

- All order operations (except the Vipps callback) require a valid JWT in the `Authorization` header:
  ```http
  Authorization: Bearer <access_token>
  Content-Type: application/json
  ```
- Customers may list and create their own orders; admins may update or delete any order.

---

## List Orders

**GET** `/orders/`

Query parameters:
- `skip` (int, optional): offset for pagination (default 0)
- `limit` (int, optional): number of orders to return (default 100)

Example:
```http
GET http://localhost:8000/orders/?skip=0&limit=10
Authorization: Bearer <customer_token>
```
Response (200 OK):
```json
[
  {
    "id": 5,
    "customer_id": 3,
    "total_amount": 149.98,
    "status": "pending",
    "created_at": "2025-06-08T22:10:15Z",
    "items": [ ... ]
  },
  ...
]
```

---

## Get Order Details

**GET** `/orders/{order_id}`

Example:
```http
GET http://localhost:8000/orders/5
Authorization: Bearer <customer_token>
```
Response (200 OK):
```json
{
  "id": 5,
  "customer_id": 3,
  "total_amount": 149.98,
  "status": "pending",
  "created_at": "2025-06-08T22:10:15Z",
  "items": [
    { "id": 12, "product_id": 7, "quantity": 2, "price": 74.99 }
  ]
}
```

---

## Create a New Order

**POST** `/orders/`

Request body:
```json
{
  "customer_id": 3,
  "items": [
    { "product_id": 7, "quantity": 2 },
    { "product_id": 9, "quantity": 1 }
  ]
}
```
Example:
```http
POST http://localhost:8000/orders/
Authorization: Bearer <customer_token>
```
Response (201 Created):
```json
{
  "id": 6,
  "customer_id": 3,
  "total_amount": 299.97,
  "status": "pending",
  "created_at": "2025-06-08T22:20:00Z",
  "items": [
    { "id": 13, "product_id": 7, "quantity": 2, "price": 74.99 },
    { "id": 14, "product_id": 9, "quantity": 1, "price": 149.99 }
  ]
}
```

---

## Initiate a Vipps Payment

**POST** `/orders/{order_id}/pay`

Request body:
```json
{
  "callback_url": "https://your-frontend.com/payments/callback",
  "shipping": { ... }
}
```
- `callback_url`: URL Vipps will POST payment status to
- `shipping`: optional if user has profile

Example:
```http
POST http://localhost:8000/orders/6/pay
Authorization: Bearer <customer_token>
```
Response (200 OK):
```json
{
  "data": {
    "orderId": "6",
    "paymentId": "abc123",
    "status": "CREATED",
    "url": "https://apitest.vipps.no/checkout/...?reference=..."
    // additional Vipps fields
  }
}
```

---

## Handle Vipps Callback

**POST** `/orders/{order_id}/callback`

Vipps will send payment status updates here:
```json
{
  "transactionStatus": "SETTLED",
  "orderId": "6"
}
```
- No auth required (Vipps server calls this endpoint)
- On `AUTHORIZED` or `SETTLED`, order status becomes `paid`; on `REJECTED`, status becomes `canceled`.

Response: `204 No Content`

---

## Update Order Status (Admin Only)

**PUT** `/orders/{order_id}/status?status=<new_status>`

- Valid statuses: `pending`, `paid`, `shipped`, `canceled`, `refunded`

Example:
```http
PUT http://localhost:8000/orders/6/status?status=shipped
Authorization: Bearer <admin_token>
```
Response (200 OK):
```json
{
  "id": 6,
  "customer_id": 3,
  "total_amount": 299.97,
  "status": "shipped",
  "created_at": "...",
  "items": [...]
}
```

---

## Delete an Order (Admin Only)

**DELETE** `/orders/{order_id}`

- Restores stock quantities for deleted items

Example:
```http
DELETE http://localhost:8000/orders/6
Authorization: Bearer <admin_token>
```
Response: `204 No Content`

---

All endpoints support CORS from `http://localhost:3000` and `http://localhost:3001`.Ensure you include the `Authorization` header for protected routes.
