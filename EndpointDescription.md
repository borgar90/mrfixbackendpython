# API Endpoint Reference

Below is an overview of all available endpoints in the Webshop API, including HTTP method, URL path, purpose, and authentication/authorization requirements.

## Authentication

| Method | Path       | Description                         | Auth        |
|--------|------------|-------------------------------------|-------------|
| GET    | `/`        | Health check                        | Public      |
| POST   | `/token`   | Obtain JWT access token (OAuth2)    | Public      |

### Authentication Endpoints Explained
- **GET `/`**: Returns a simple JSON health check ({ "message": "Webshop API is up and running!" }).
- **POST `/token`**: Accepts form data `username` and `password`, validates credentials, and returns a JWT access token for subsequent authenticated requests.

## Users

| Method | Path               | Description                        | Auth           |
|--------|--------------------|------------------------------------|----------------|
| POST   | `/users/`          | Register new user (admin or cust); accept optional shipping data for customers | Public         |
| GET    | `/users/`          | List all users                     | Admin only     |
| GET    | `/users/me`        | Get profile of the current user    | Authenticated  |
| GET    | `/users/{id}`      | Get user by ID                     | Admin only     |
| PUT    | `/users/{id}`      | Update user                        | Admin only     |
| DELETE | `/users/{id}`      | Delete user                        | Admin only     |

### User Endpoints Explained
- **POST `/users/`**: Registers a new user and optional customer shipping profile. Expects JSON:
  ```json
  {
    "email": "user@example.com",
    "password": "secret",
    "role": "customer",
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
  If `role` is `customer` and `shipping` is provided, creates a corresponding customer record.
- **GET `/users/me`**: Retrieves the profile of the current authenticated user, including email and role (and shipping/customer profile if exists). Requires a valid JWT.
- **GET `/users/`**: Returns a list of all user profiles. Admin-only access.
- **GET `/users/{id}`**: Retrieves a specific user by ID. Admin-only.
- **PUT `/users/{id}`**: Updates an existing user’s email, password, or role. Admin-only.
- **DELETE `/users/{id}`**: Deletes a user account from the system. Admin-only.

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

### Customer Endpoints Explained
- **POST `/customers/`**: Creates a new customer profile with personal details; admin-only.
- **GET `/customers/`**: Lists all customer profiles. Admin-only.
- **GET `/customers/{id}`**: Retrieves details for one customer by ID. Admin-only.
- **PUT `/customers/{id}`**: Updates a customer’s personal information. Admin-only.
- **DELETE `/customers/{id}`**: Removes a customer profile. Admin-only.
- **GET `/customers/me`**: Returns the authenticated customer’s own profile. Requires a valid JWT.
- **DELETE `/customers/me`**: Deletes or anonymizes the authenticated user’s data for GDPR compliance. Requires JWT.

## Products

| Method | Path                                | Description                          | Auth           |
|--------|-------------------------------------|--------------------------------------|----------------|
| GET    | `/products/`                        | List products                        | Public         |
| GET    | `/products/{id}`                    | Get product by ID                    | Public         |
| POST   | `/products/`                        | Create new product                   | Admin only     |
| PUT    | `/products/{id}`                    | Update product                       | Admin only     |
| DELETE | `/products/{id}`                    | Delete product                       | Admin only     |
| POST   | `/products/{id}/stock`              | Adjust stock (± quantity)            | Admin only     |
| GET    | `/products/{id}/images`             | List all images for a product        | Public         |
| GET    | `/products/{id}/images/{image_id}`  | Get a single image by ID             | Public         |
| POST   | `/products/{id}/images`             | Upload a new product image           | Admin only     |
| PUT    | `/products/{id}/images/{image_id}`  | Update image flags (main, thumbnail) | Admin only     |
| DELETE | `/products/{id}/images/{image_id}`  | Delete a product image               | Admin only     |

### Product Endpoints Explained
- **GET `/products/`**: Returns a paginated list of products with price and stock.
- **GET `/products/{id}`**: Retrieves one product’s details. Public.
- **POST `/products/`**: Creates a new product record (name, price, stock). Admin-only.
- **PUT `/products/{id}`**: Updates product fields such as price, description, or stock. Admin-only.
- **DELETE `/products/{id}`**: Deletes a product. Admin-only.
- **POST `/products/{id}/stock`**: Adjusts stock levels by a positive or negative quantity. Admin-only.
- **GET `/products/{id}/images`**: Retrieves all image records for a product. Public.
- **GET `/products/{id}/images/{image_id}`**: Retrieves a single product image. Public.
- **POST `/products/{id}/images`**: Uploads a new image file and creates a database record. Admin-only.
- **PUT `/products/{id}/images/{image_id}`**: Updates the `is_main` or `is_thumbnail` flags on an image. Admin-only.
- **DELETE `/products/{id}/images/{image_id}`**: Deletes an image record and removes the file. Admin-only.

## Orders

| Method | Path                             | Description                         | Auth           |
|--------|----------------------------------|-------------------------------------|----------------|
| GET    | `/orders/`                       | List orders (paginated)             | Authenticated  |
| GET    | `/orders/{id}`                   | Get order details                   | Authenticated  |
| POST   | `/orders/`                       | Place a new order                   | Authenticated  |
| PUT    | `/orders/{id}/status`            | Update order status                 | Admin only     |
| DELETE | `/orders/{id}`                   | Delete order (restores stock)       | Admin only     |
| POST   | `/orders/{order_id}/callback`    | Handle Vipps payment status callback | Public         |

### Order Endpoints Explained
- **GET `/orders/`**: Retrieves all orders for the authenticated user with pagination.
- **GET `/orders/{id}`**: Retrieves details of one order, including items and totals.
- **POST `/orders/`**: Places a new order by specifying `customer_id` and `items` array; returns created order.
- **PUT `/orders/{id}/status`**: Updates order status (e.g., to shipped or canceled). Admin-only.
- **DELETE `/orders/{id}`**: Deletes an order and restores product stock. Admin-only.
- **POST `/orders/{order_id}/callback`**: Endpoint for Vipps to notify payment status changes; updates order status accordingly.

## CRM Notes

| Method | Path                    | Description                         | Auth           |
|--------|-------------------------|-------------------------------------|----------------|
| POST   | `/crm/notes`            | Create a CRM note                   | Authenticated  |
| GET    | `/crm/notes/{cust_id}`  | List notes for a customer           | Authenticated  |

### CRM Endpoints Explained
- **POST `/crm/notes`**: Creates a support note attached to a customer; requires JWT.
- **GET `/crm/notes/{cust_id}`**: Retrieves all CRM notes for the specified customer ID; requires JWT.

## Statistics

| Method | Path                                    | Description                             | Auth        |
|--------|-----------------------------------------|-----------------------------------------|-------------|
| GET    | `/statistics/sales/{year}`              | Monthly sales totals for given year     | Admin only  |
| GET    | `/statistics/unprocessed_orders`        | List all pending orders                 | Admin only  |
| GET    | `/statistics/total_users`                | Total number of registered users        | Admin only  |
| GET    | `/statistics/paid_unprocessed_count`    | Count of paid but unprocessed orders    | Admin only  |
| GET    | `/statistics/total_orders`               | Total number of orders placed           | Admin only  |
| GET    | `/statistics/total_revenue`              | Total revenue from paid orders (excluding refunds)  | Admin only  |

### Statistics Endpoints Explained
- **GET `/statistics/sales/{year}`**: Returns total sales aggregated by month for the given year.
- **GET `/statistics/unprocessed_orders`**: Lists all orders still in `pending` status.
- **GET `/statistics/total_users`**: Returns the total count of registered users.
- **GET `/statistics/paid_unprocessed_count`**: Returns the count of orders paid but not yet processed.
- **GET `/statistics/total_orders`**: Returns the total count of all orders placed.
- **GET `/statistics/total_revenue`**: Returns the sum of `total_amount` from orders with a `paid` status.

## Payment

| Method | Path                       | Description                                   | Auth          |
|--------|----------------------------|-----------------------------------------------|---------------|
| POST   | `/payment/vipps/initiate`  | Initiate a Vipps payment for a pending order  | Authenticated |

---
Generated on: June 8, 2025