# API Endpoint Reference

Below is an overview of all available endpoints in the Webshop API, including HTTP method, URL path, purpose, and authentication/authorization requirements.

## Authentication

| Method | Path       | Description                         | Auth        |
|--------|------------|-------------------------------------|-------------|
| GET    | `/`        | Health check                        | Public      |
| POST   | `/token`   | Obtain JWT access token (OAuth2)    | Public      |

## Users

| Method | Path               | Description                        | Auth           |
|--------|--------------------|------------------------------------|----------------|
| POST   | `/users/`          | Register new user (admin or cust)  | Public         |
| GET    | `/users/`          | List all users                     | Admin only     |
| GET    | `/users/{id}`      | Get user by ID                     | Admin only     |
| PUT    | `/users/{id}`      | Update user                        | Admin only     |
| DELETE | `/users/{id}`      | Delete user                        | Admin only     |

## Customers

| Method | Path                         | Description                           | Auth           |
|--------|------------------------------|---------------------------------------|----------------|
| POST   | `/customers/`                | Create a customer profile             | Admin only     |
| GET    | `/customers/`                | List all customers                    | Admin only     |
| GET    | `/customers/{id}`            | Get customer by ID                    | Admin only     |
| PUT    | `/customers/{id}`            | Update customer                       | Admin only     |
| DELETE | `/customers/{id}`            | Delete customer                       | Admin only     |
| GET    | `/customers/me`             | Get own customer profile              | Authenticated  |
| DELETE | `/customers/me`             | Delete/anonymize own data (GDPR)      | Authenticated  |

## Products

| Method | Path                          | Description                          | Auth           |
|--------|-------------------------------|--------------------------------------|----------------|
| GET    | `/products/`                  | List products                        | Public         |
| GET    | `/products/{id}`              | Get product by ID                    | Public         |
| POST   | `/products/`                  | Create new product                   | Admin only     |
| PUT    | `/products/{id}`              | Update product                       | Admin only     |
| DELETE | `/products/{id}`              | Delete product                       | Admin only     |
| POST   | `/products/{id}/stock`        | Adjust stock (± quantity)            | Admin only     |

## Orders

| Method | Path                             | Description                         | Auth           |
|--------|----------------------------------|-------------------------------------|----------------|
| GET    | `/orders/`                       | List orders (paginated)             | Authenticated  |
| GET    | `/orders/{id}`                   | Get order details                   | Authenticated  |
| POST   | `/orders/`                       | Place a new order                   | Authenticated  |
| PUT    | `/orders/{id}/status`            | Update order status                 | Admin only     |
| DELETE | `/orders/{id}`                   | Delete order (restores stock)       | Admin only     |

## CRM Notes

| Method | Path                    | Description                         | Auth           |
|--------|-------------------------|-------------------------------------|----------------|
| POST   | `/crm/notes`            | Create a CRM note                   | Authenticated  |
| GET    | `/crm/notes/{cust_id}`  | List notes for a customer           | Authenticated  |

## Statistics

| Method | Path                                    | Description                             | Auth        |
|--------|-----------------------------------------|-----------------------------------------|-------------|
| GET    | `/statistics/sales/{year}`              | Monthly sales totals for given year     | Admin only  |
| GET    | `/statistics/unprocessed_orders`        | List all pending orders                 | Admin only  |

---
Generated on: June 7, 2025