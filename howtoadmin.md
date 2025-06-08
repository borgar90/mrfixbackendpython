# How to Create an Admin Account

This guide explains how to obtain or create an administrator account for the Webshop API.

## 1. Built-in Default Admin

On application startup, the API automatically ensures a default admin user exists.
- **Email (username)**: `admin`
- **Password**: `adminpass`

To verify or use this default admin:
1. Start the server:  
   ```powershell
   uvicorn app.main:app --reload
   ```
2. Obtain a token:
   ```http
   POST /token
   Content-Type: application/x-www-form-urlencoded

   username=admin&password=adminpass
   ```
3. Use the returned `access_token` in the `Authorization: Bearer <token>` header for admin-only endpoints.

## 2. Registering a New Admin via API

You can create additional admin accounts using the public user registration endpoint.

**Request**:
```http
POST /users/
Content-Type: application/json

{
  "email": "newadmin@example.com",
  "password": "securepass",
  "role": "admin"
}
```

- No authentication is required to call this endpoint (public access).
- Fields:
  - `email`: unique email for the admin user.
  - `password`: plaintext password (will be hashed).
  - `role`: must be `"admin"` to grant admin privileges.

After registration, obtain a token using `/token` and the new admin’s credentials.

## 3. Adding Admin Directly in the Database

If you prefer direct DB access (e.g., via MySQL client or migration tool), insert a record into the `users` table:
```sql
INSERT INTO users (email, hashed_password, role, created_at)
VALUES (
  'admin2@example.com',
  '<bcrypt_hashed_password>',
  'admin',
  NOW()
);
```

- Use a bcrypt hash for `hashed_password` (you can generate one with a small Python snippet):
  ```python
  from passlib.context import CryptContext
  pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
  print(pwd.hash("securepass"))
  ```
- After insertion, issue the token via `/token` endpoint as described above.

## MySQL Schema Migration for Shipping Data

If you are using a MySQL database and have existing tables, you need to add the `user_id` column and foreign key to the `customers` table to support shipping data on user registration.

Run the following SQL commands in your MySQL client:

```sql
ALTER TABLE customers
  ADD COLUMN user_id INT NULL;

ALTER TABLE customers
  ADD CONSTRAINT fk_customers_user_id
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE;
```

After applying these, restart the FastAPI app. New users registered with shipping info will be linked correctly.

If you prefer automatic migrations, consider integrating Alembic:
1. `alembic init migrations`
2. Configure `alembic.ini` and `env.py`.
3. `alembic revision --autogenerate -m "Add user_id to customers"`
4. `alembic upgrade head`

---
_End of admin creation guide._