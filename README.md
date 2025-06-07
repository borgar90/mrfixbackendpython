# Webshop API

A FastAPI-based e-commerce backend featuring:

- Customer management (CRUD)
- Product catalog (CRUD)
- Order processing with order items, pricing, and stock management
- CRM notes for customers
- JWT-based authentication and role-based access control (admin vs. customer)
- In-memory SQLite testing setup
- Integrations placeholder for Bring shipping and Vipps payment

## Features

- **Customers**: Create, read, update, delete customers
- **Products**: Create, read, update, delete products
- **Orders**: Place new orders, view order details, update status, delete orders
- **CRM**: Create and list notes for customers
- **Authentication**: OAuth2 password flow, JWT tokens, admin vs. user roles

## Requirements

- Python 3.10+
- Dependencies defined in `requirements.txt`

## Installation

1. Clone the repository:
   ```powershell
   git clone <repo_url>
   cd mrfixweb\backend
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`:
   ```properties
   MYSQL_USER=...
   MYSQL_PASSWORD=...
   MYSQL_HOST=...
   MYSQL_PORT=...
   MYSQL_DATABASE=...
   JWT_SECRET_KEY=your_secret_key
   VIPPS_CLIENT_ID=...
   VIPPS_CLIENT_SECRET=...
   VIPPS_SANDBOX_URL=...
   VIPPS_PRODUCTION_URL=...
   BRING_API_KEY=...
   BRING_API_URL=...
   ```

## Running the Application

Start the API server with Uvicorn:
```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Interactive Swagger UI:  `http://127.0.0.1:8000/docs`  
ReDoc:  `http://127.0.0.1:8000/redoc`

### Authentication

1. Obtain access token:
   ```http
   POST /token
   Content-Type: application/x-www-form-urlencoded

   grant_type=&username=admin&password=adminpass&scope=&client_id=&client_secret=
   ```
2. Copy the `access_token` from response.
3. For protected endpoints, add header:
   ```http
   Authorization: Bearer <access_token>
   ```

### Endpoints

#### Public (no auth)
- `GET /products`  
- `GET /products/{id}`  
- `GET /` (health check)

#### Authenticated (any user)
- `POST /orders`  
- `GET /orders`  
- `GET /orders/{id}`  
- `GET /customers`  
- `GET /customers/{id}`  
- `POST /crm/notes`  
- `GET /crm/notes/{customer_id}`  

#### Admin only
- `POST /products`  
- `PUT /products/{id}`  
- `DELETE /products/{id}`  
- `POST /customers`  
- `PUT /customers/{id}`  
- `DELETE /customers/{id}`  
- `PUT /orders/{id}/status`  
- `DELETE /orders/{id}`  

## Testing

Unit and integration tests use pytest with an in-memory SQLite database. To run tests:
```powershell
pytest
```

---
_Backend service for MRFixWeb webshop project._