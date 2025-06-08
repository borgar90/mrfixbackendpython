# Authentication Reference

This document describes the authentication and authorization mechanisms used in the Webshop API.

## 1. OAuth2 Password Flow (/token)

- **Endpoint**: `POST /token`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Form fields**:
  - `username`: user email (or literal `admin` for built-in admin)
  - `password`: user password
- **Response**: JSON with `access_token` and `token_type: bearer`.

Behavior:
- For credentials `admin` / `adminpass`, bypass DB lookup and issue an admin token.
- For other users, validates against the `users` table (checks hashed password).

## 2. JWT Token Generation (`create_access_token`)

- **Secret**: `JWT_SECRET_KEY` (from environment, default `changeme`).
- **Algorithm**: `HS256`.
- **Expiry**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Payload claims**:
  - `sub`: subject (user email or `admin`)
  - `role`: user role string (`admin` or `customer`)
  - `exp`: expiration timestamp (UTC) using timezone-aware datetime.

## 3. Dependency: `get_current_user`

Used to protect endpoints for authenticated users.

1. Extracts token via `OAuth2PasswordBearer(tokenUrl="/token")`.
2. Decodes and verifies signature and expiry.
3. Reads `sub` and `role` from JWT payload.
4. Returns a SQLAlchemy `User` model instance with these attributes:
   - `User.email = sub`
   - `User.role = role`

_Note_: No DB lookup is performed for `admin`; all other emails must exist in the DB.

## 4. Dependency: `get_current_admin`

Wraps `get_current_user` to enforce admin-only access:
- Checks `current_user.role == "admin"`.
- Raises HTTP 403 if the role is not admin.

## 5. Default Admin Creation (App Lifespan)

On application startup (using a FastAPI **lifespan** handler):
- Checks if a user with `email='admin'` exists.
- If not, creates a new `User` record with:
  - `email = 'admin'`
  - `hashed_password` of `'adminpass'`
  - `role = 'admin'`

This ensures a built-in admin account for initial access and automated tests.

## 6. Password Hashing & Verification

- Uses **Passlib** `CryptContext` with the `bcrypt` scheme.
- **`pwd_context.hash(password)`** for storing hashed passwords.
- **`pwd_context.verify(plain, hashed)`** for checking credentials.


---
_Authentication implementation details are in `app/auth.py`._