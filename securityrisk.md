# Security Risk Report

This document outlines potential security issues and risks in the current Webshop API implementation, along with recommendations for mitigation.

1. Default Credentials & Secrets
   - **Hardcoded admin credentials**: `admin:adminpass` is created by default in code. An attacker aware of this can gain admin access immediately.
   - **Weak JWT secret fallback**: The code uses `JWT_SECRET_KEY` defaulting to `changeme` if environment variable is missing. This secret is trivial to guess.
   - Recommendation: Remove hardcoded credentials, force environment-based admin setup, and require a strong, random JWT_SECRET_KEY.

2. Authentication & Password Policies
   - **No password complexity enforcement**: User passwords are only hashed, but no checks for minimum length or complexity.
   - **No rate limiting/brute-force protection**: The `/token` endpoint allows unlimited login attempts.
   - Recommendation: Implement password strength validation, account lockouts or rate limiting on login, and consider CAPTCHA for public registration.

3. File Upload Handling
   - **Unrestricted file types and content**: `upload_image` saves any uploaded file extension without validation.
   - **No file size limits**: Large files could be uploaded, leading to denial-of-service or storage exhaustion.
   - **Directory traversal risk**: Although filenames are randomly generated, the dynamic product folder path uses `os.getcwd()`, potentially exploitable in misconfigured deployments.
   - Recommendation: Validate MIME types/extensions, enforce maximum file size, and use a dedicated upload directory outside the application root.

4. CORS Configuration
   - **Wide-open development origins**: CORS allows only `localhost` origins, but in production this may be misconfigured or overly permissive.
   - Recommendation: Ensure CORS is locked down to trusted frontend domains in production and disable it for untrusted origins.

5. Lack of Transport Security Enforcement
   - **No HTTPS enforcement**: The API does not redirect or require TLS; sensitive data (tokens, passwords) may be exposed over plain HTTP.
   - Recommendation: Deploy behind HTTPS and configure HSTS.

6. Input Validation & Injection
   - **Limited schema validation**: While Pydantic schemas validate JSON shapes, fields like `description` or `address` are free-text; potential for XSS if rendered in a front-end without sanitization.
   - **Raw SQL migrations**: The manual `ALTER TABLE` statements use raw SQL without sanitization context; be cautious of SQL injection if user input ever reaches that path.
   - Recommendation: Sanitize free-text fields before display, use parameterized queries exclusively, and migrate to a managed migration tool (Alembic).

7. Payment Callback Security
   - **No signature verification**: The Vipps callback trusts incoming JSON without verifying authenticity or HMAC signature.
   - Recommendation: Validate callback requests against known Vipps signatures or secrets to prevent spoofed payment updates.

8. Sensitive Data Exposure
   - **Verbose error messages**: SQLAlchemy errors and tracebacks can leak internal database structure.
   - Recommendation: Hide internal error details in production and implement a custom exception handler.

9. Other Considerations
   - **No CSRF protection**: While JWT mitigates some risks, any browser-based form submissions without CSRF tokens may be vulnerable.
   - **Session management**: Tokens expire after 30 minutes; consider refresh tokens or revocation lists for better control.

---
**Next Steps**: Review each area, implement the recommendations, and perform a security audit or penetration test before production rollout.
