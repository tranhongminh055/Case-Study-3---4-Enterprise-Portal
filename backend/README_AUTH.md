# Authentication & Authorization System (AUTH_DB)

**Status**: Production-Ready | **JWT Version**: HS256 | **Password Hashing**: bcrypt | **Token Expiration**: 45 minutes

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Database Requirements](#database-requirements)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [Security Requirements](#security-requirements)
6. [Audit Logging & Monitoring](#audit-logging--monitoring)
7. [Environment Configuration](#environment-configuration)
8. [Security Testing & Validation](#security-testing--validation)
9. [Token Management](#token-management)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1) Create environment file

Copy `backend/.env.example` to `backend/.env` and edit values (especially `AUTH_JWT_SECRET` and database credentials).

```powershell
Copy-Item backend\.env.example backend\.env
```

**Critical settings for production:**
- `AUTH_JWT_SECRET`: Use a strong, randomly generated secret (min 32 characters)
- `AUTH_JWT_EXP_MINUTES`: Set between 30-60 minutes
- Ensure `BOOTSTRAP_ADMIN_USERNAME` and `BOOTSTRAP_ADMIN_PASSWORD` are changed

### 2) Install dependencies and initialize AUTH_DB

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/scripts/init_auth_db.py
```

This will create the AUTH_DB tables (default: `backend/auth_db.sqlite`) and bootstrap an Admin user from your `.env`.

### 3) Run server

```powershell
# Development (with reload)
uvicorn backend.main:app --reload --port 8000

# Production (with HTTPS/TLS 1.3)
uvicorn backend.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

### 4) Run tests

```powershell
pytest backend/tests -q
```

### 5) Register users

- Public endpoint: `POST /auth/register` accepts JSON:
  ```json
  {
    "username": "user@example.com",
    "password": "Secret1!",
    "role": "Employee"
  }
  ```
- If `role` is omitted, the new user will be created with role `Employee`
- Admins may create other roles by specifying `role` when creating accounts
- Passwords are hashed with bcrypt; plaintext passwords are never logged

---

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
Create a new user account. Public endpoint (no authentication required).

**Request:**
```json
{
  "username": "john.doe@example.com",
  "password": "SecurePassword123!",
  "role": "Employee"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | Unique email or identifier |
| password | string | Yes | Plaintext password (will be hashed with bcrypt) |
| role | string | No | Default: "Employee". Allowed: Admin, HR Manager, Payroll Manager, Employee |

**Responses:**
- `201 Created`: User successfully registered
  ```json
  {
    "user_id": 1,
    "username": "john.doe@example.com",
    "role": "Employee"
  }
  ```
- `400 Bad Request`: Missing username or password
- `409 Conflict`: Username already exists

**Security Notes:**
- Password must meet complexity requirements (min 8 chars, uppercase, lowercase, number, special char)
- Account is created but not automatically logged in
- Audit event logged to `AUTH_DB.Logs` table

---

#### POST /auth/login
Authenticate a user and issue a JWT token.

**Request:**
```json
{
  "username": "john.doe@example.com",
  "password": "SecurePassword123!"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | Username or email |
| password | string | Yes | Plaintext password |

**Responses:**
- `200 OK`: Login successful
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "Employee"
  }
  ```
- `401 Unauthorized`: Invalid username or password
  - Failed attempt logged with source IP for brute-force detection

**Token Details:**
- Format: JWT with HS256 algorithm
- Expiration: 45 minutes (configurable via `AUTH_JWT_EXP_MINUTES`)
- Contains: `sub` (user_id), `jti` (JWT ID), `role`, `username`, `iat`, `exp`
- Token ID (JTI) stored in `AUTH_DB.Tokens` for revocation tracking

**Security Notes:**
- Token issued after successful bcrypt password verification
- Failed login attempts tracked in audit log for security monitoring
- Implement rate limiting to prevent brute-force attacks

---

#### POST /auth/logout
Revoke the current JWT token (add to blacklist).

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Responses:**
- `200 OK`: Logout successful
  ```json
  {
    "status": "ok"
  }
  ```
- `401 Unauthorized`: Missing or invalid token

**Security Notes:**
- Token marked as revoked in database
- Revoked token cannot be used for further API calls
- Audit event logged with timestamp and user identity
- Client must discard the token locally

---

#### POST /auth/refresh
Refresh an expired or about-to-expire JWT token.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Responses:**
- `200 OK`: Token refreshed successfully
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
- `401 Unauthorized`: Token revoked, invalid, or expired

**Token Refresh Logic:**
1. Old token validated (not revoked, not expired)
2. Old token marked as revoked
3. New token issued with same user_id, role, username
4. New token gets fresh expiration timestamp
5. Both tokens tracked separately via JTI

**Use Cases:**
- User performing long-lived operations (upload, data import)
- Prevent forced logout after 45 minutes of inactivity
- Sliding window session management

**Security Notes:**
- Old token immediately invalidated upon refresh
- Implements token rotation for enhanced security
- Refresh attempts logged in audit trail

---

## Database Requirements

### AUTH_DB Schema

#### Users Table (`auth_users`)
Stores authenticated user credentials and roles.

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | Integer | PK, Auto-increment | Unique user identifier |
| username | String(150) | UNIQUE, NOT NULL | Email or username for login |
| password_hash | String(512) | NOT NULL | Bcrypt-hashed password (never plaintext) |
| role | String(50) | NOT NULL | User role (Admin, HR Manager, Payroll Manager, Employee) |
| created_at | DateTime | NOT NULL, Default=NOW | Account creation timestamp |

**Constraints:**
- Username must be unique
- Password hash must be non-empty
- Role must be one of allowed values

---

#### Tokens Table (`auth_tokens`)
Tracks issued JWT tokens for revocation and validation.

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | Integer | PK, Auto-increment | Unique token record ID |
| user_id | Integer | FK(auth_users.id), NOT NULL | Token owner |
| jti | String(256) | UNIQUE, NOT NULL | JWT ID (unique token identifier) |
| expires_at | DateTime | NOT NULL | Token expiration time |
| revoked | Boolean | NOT NULL, Default=False | Revocation status |

**Constraints:**
- Foreign key to `auth_users` table
- JTI must be unique (prevents token reuse)
- Revocation checked on every API request

**Maintenance:**
- Expired tokens (past `expires_at`) can be archived or deleted after 90 days
- Revoked tokens kept for audit trail (90-day retention)

---

#### Logs Table (`auth_logs`)
Comprehensive audit trail for security events.

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | Integer | PK, Auto-increment | Log entry ID |
| timestamp | DateTime | NOT NULL, Default=NOW | Event timestamp (UTC) |
| user_id | Integer | FK(auth_users.id), Nullable | User who performed action |
| username | String(150) | Nullable | Username (cached for deleted accounts) |
| action | String(100) | NOT NULL | Action type (login, logout, refresh, get, post, etc.) |
| endpoint | String(300) | Nullable | API endpoint called |
| result | String(50) | NOT NULL | Result (success, failure, 401, 403, 400, etc.) |
| source_ip | String(100) | Nullable | Client IP address for geographic tracking |
| details | Text | Nullable | Additional context (error messages, details) |

**Constraints:**
- Never log plaintext passwords or sensitive data
- All timestamps in UTC
- Source IP used for brute-force detection
- User ID can be NULL for unauthenticated requests

**Log Retention Policy:**
- Keep logs for 90 days minimum
- After 90 days, archive or delete (per compliance requirements)
- Consider database size when implementing retention

---

### Password Security

**Hashing Algorithm:** bcrypt with salt (10-12 rounds)

**Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (@, !, #, $, %, etc.)

**Validation:**
```python
from backend.utils.security import hash_password, verify_password

# Hashing
hashed = hash_password("UserPassword123!")

# Verification
is_valid = verify_password("UserPassword123!", hashed)
```

**Security Notes:**
- Passwords never stored in plaintext
- Bcrypt salt generated automatically
- Hash verified using constant-time comparison
- Failed verification logged without revealing details

---

## Role-Based Access Control (RBAC)

### Role Definitions

| Role | Description | Access Level | Permissions |
|------|-------------|--------------|-------------|
| **Admin** | System administrator | Full | All endpoints, all data, user management |
| **HR Manager** | Human Resources management | Limited | HR data (HUMAN_2025 database), employees, departments, positions |
| **Payroll Manager** | Payroll administration | Limited | Payroll data, salary, attendance, reports |
| **Employee** | Regular employee | Minimal | View own profile, own salary, personal attendance |

### Access Control Matrix

| Endpoint | Admin | HR Manager | Payroll Manager | Employee |
|----------|-------|-----------|-----------------|----------|
| `/employees` (GET all) | ✅ | ✅ | ❌ | ❌ |
| `/employees/{id}` (GET) | ✅ | ✅ | ❌ | ✅ (own) |
| `/employees` (POST/PUT/DELETE) | ✅ | ✅ | ❌ | ❌ |
| `/departments` | ✅ | ✅ | ❌ | ❌ |
| `/positions` | ✅ | ✅ | ❌ | ❌ |
| `/payroll` | ✅ | ❌ | ✅ | ✅ (own) |
| `/reports` | ✅ | ✅ | ✅ | ✅ (own) |

### Enforcement

**Dependency Injection:**
```python
from fastapi import Depends
from backend.utils.rbac import require_roles, require_auth

@router.get("/employees")
def get_employees(auth = Depends(require_roles(["Admin", "HR Manager"]))):
    """Only Admin and HR Manager can access all employees"""
    pass

@router.get("/employees/{employee_id}")
def get_employee(employee_id: int, 
                auth = Depends(require_self_or_roles(
                    "employee_id", 
                    ["Admin", "HR Manager"]))):
    """Admin, HR Manager, or the employee viewing their own record"""
    pass
```

**Token-Based Authorization:**
- Role embedded in JWT token
- Validated on every request
- Admin role bypasses all role checks

---

## Security Requirements

### HTTPS/TLS Configuration

**Requirement:** All production deployments must use HTTPS with TLS 1.3.

**Development Setup (Self-Signed Certificate):**
```powershell
# Generate self-signed certificate (90 days)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 90 -nodes

# Run with HTTPS
uvicorn backend.main:app --host 0.0.0.0 --port 443 `
  --ssl-keyfile=./key.pem `
  --ssl-certfile=./cert.pem
```

**Production Setup (Let's Encrypt):**
```bash
# Use certbot to obtain free SSL certificate
certbot certonly --standalone -d your-domain.com

# Use certificate path in production
uvicorn backend.main:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile=/etc/letsencrypt/live/your-domain.com/privkey.pem \
  --ssl-certfile=/etc/letsencrypt/live/your-domain.com/fullchain.pem
```

**Proxy Configuration (Nginx/Apache):**
```nginx
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Authorization $http_authorization;
        proxy_pass_header Authorization;
    }
}
```

### Environment Variables

**Required for Security:**
```bash
# JWT Configuration
AUTH_JWT_SECRET=use-strong-random-secret-min-32-chars
AUTH_JWT_EXP_MINUTES=45              # 30-60 minute recommended
AUTH_JWT_ALGO=HS256                  # Algorithm (HS256, RS256)

# Bootstrap Admin (change immediately after first login)
BOOTSTRAP_ADMIN_USERNAME=admin@company.com
BOOTSTRAP_ADMIN_PASSWORD=TempPassword123!
```

**Optional:**
```bash
# Custom database URL (defaults to sqlite)
AUTH_DB_URL=postgresql://user:pass@localhost/auth_db

# Frontend CORS (restrict to your domain)
FRONTEND_ORIGIN=https://app.company.com,https://mobile.company.com
```

### Password Policy Enforcement

**Implement at Registration:**
```python
import re

def validate_password(password: str) -> bool:
    """Enforce password complexity requirements"""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain lowercase letter")
    if not re.search(r'\d', password):
        raise ValueError("Password must contain number")
    if not re.search(r'[!@#$%^&*]', password):
        raise ValueError("Password must contain special character")
    return True
```

### Token Security

**JWT Configuration:**
- Algorithm: HS256 (HMAC with SHA-256)
- Expiration: 45 minutes
- Includes: User ID, Role, Username, Issued At, Expiration
- JTI (JWT ID) for tracking and revocation

**Token Storage (Client-Side - Frontend):**
- Store in memory (not localStorage - XSS safe)
- Include in `Authorization: Bearer <TOKEN>` header
- Remove from memory on logout
- DO NOT store in cookies without HttpOnly flag

**Token Rotation:**
- Old token revoked when new token issued via `/auth/refresh`
- Prevents token replay attacks
- Automatic session extension without re-authentication

---

## Audit Logging & Monitoring

### Logged Events

Every security-relevant event is logged to `AUTH_DB.Logs`:

| Event | Details Logged | Alert Threshold |
|-------|---|---|
| Login Success | User ID, username, IP, timestamp | None |
| Login Failure | Attempted username, IP, timestamp | 5+ in 15 min = brute-force |
| Logout | User ID, IP, timestamp | None |
| Token Refresh | User ID, old JTI, new JTI | None |
| Unauthorized Access (401) | Attempted endpoint, IP | 10+ in 5 min |
| Forbidden Access (403) | User ID, endpoint, required role | Monitor for IDOR attempts |
| API Call (GET/POST/PUT/DELETE) | User ID, method, endpoint, status | 500 errors |

### Monitoring Dashboard Queries

**Brute-force Detection:**
```sql
-- Login failures by IP in last 15 minutes
SELECT source_ip, COUNT(*) as failed_attempts
FROM auth_logs
WHERE action = 'login' AND result = 'failure'
  AND timestamp > NOW() - INTERVAL 15 MINUTE
GROUP BY source_ip
HAVING failed_attempts > 5;
```

**Unauthorized Access Attempts:**
```sql
-- 401 errors in last hour (possible token attacks)
SELECT user_id, endpoint, source_ip, COUNT(*) as attempts
FROM auth_logs
WHERE result = '401'
  AND timestamp > NOW() - INTERVAL 1 HOUR
GROUP BY user_id, endpoint, source_ip;
```

**IDOR Detection:**
```sql
-- Multiple 403 errors by same user (access control bypass attempt)
SELECT user_id, username, COUNT(*) as blocked_attempts
FROM auth_logs
WHERE result = '403'
  AND timestamp > NOW() - INTERVAL 1 HOUR
GROUP BY user_id, username
HAVING blocked_attempts > 10;
```

### Log Retention

- **Active Logs**: Current + 30 days in `auth_logs` table
- **Archive**: Days 31-90 in `auth_logs_archive` (optional)
- **Deletion**: After 90 days (compliance requirement)

```sql
-- Archive old logs (example - run weekly)
INSERT INTO auth_logs_archive
SELECT * FROM auth_logs
WHERE timestamp < NOW() - INTERVAL 30 DAY;

DELETE FROM auth_logs
WHERE timestamp < NOW() - INTERVAL 90 DAY;
```

---

## Environment Configuration

### .env File

**Minimal Setup:**
```bash
# Critical - change these
AUTH_JWT_SECRET=your-secret-key-min-32-characters-here
BOOTSTRAP_ADMIN_USERNAME=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=ChangeMe123!

# Database
AUTH_DB_URL=sqlite:///./auth_db.sqlite

# Token
AUTH_JWT_EXP_MINUTES=45
```

**Production Setup:**
```bash
# Use PostgreSQL for production
AUTH_DB_URL=postgresql://authuser:securepassword@db.production.com:5432/auth_db

# Strong JWT secret (generate with: python -c "import secrets; print(secrets.token_hex(32))")
AUTH_JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# Token expiration
AUTH_JWT_EXP_MINUTES=45

# CORS for frontend
FRONTEND_ORIGIN=https://app.company.com

# Bootstrap (disable after first admin login)
BOOTSTRAP_ADMIN_USERNAME=admin@company.com
BOOTSTRAP_ADMIN_PASSWORD=use-strong-password-then-change
```

### Generate Strong JWT Secret

```powershell
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# PowerShell
[System.BitConverter]::ToString(([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))) -replace '-', ''
```

---

## Security Testing & Validation

### Functional Testing

#### Test 1: Token Issuance
```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "Test123456!",
    "role": "Employee"
  }'

# Login and get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "Test123456!"
  }'
```

**Expected Result:**
- Status 200 OK
- Response contains `access_token`, `token_type: bearer`, and role

#### Test 2: Token Expiration
```bash
# Decode JWT to check expiration
import jwt
import os

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
secret = os.getenv("AUTH_JWT_SECRET")
payload = jwt.decode(token, secret, algorithms=["HS256"])
print(f"Expires at: {payload['exp']}")
print(f"Expires in (seconds): {payload['exp'] - int(time.time())}")
```

**Expected Result:**
- Token expiration ~45 minutes from issue time
- All required claims present (sub, jti, role, username, iat, exp)

#### Test 3: Token Revocation
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login ... | jq -r '.access_token')

# Logout (revoke token)
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Try to use revoked token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/employees
```

**Expected Result:**
- Logout returns 200 OK
- Subsequent requests with revoked token return 401 Unauthorized
- Request logged as "401" in audit logs

#### Test 4: Role Enforcement
```bash
# Create employee user
curl -X POST http://localhost:8000/auth/register \
  -d '{"username": "emp@example.com", "password": "Emp123456!", "role": "Employee"}'

# Get token for employee
EMP_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login ... | jq -r '.access_token')

# Try to access admin endpoint
curl -H "Authorization: Bearer $EMP_TOKEN" \
  http://localhost:8000/admin/users
```

**Expected Result:**
- Employee request returns 403 Forbidden
- Event logged as "403" with endpoint and user ID in audit logs
- Admin can access same endpoint with their token (200 OK)

### Security Testing (OWASP-Based)

#### Test 5: SQL Injection Simulation
```bash
# Try SQL injection in username
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin\" OR \"1\"=\"1",
    "password": "anything"
  }'
```

**Expected Result:**
- Returns 401 Unauthorized (user not found)
- Login failure logged
- NO error messages revealing database details
- NO SQL error in response

**Why Safe:**
- Parameterized queries in SQLAlchemy ORM
- User input never interpolated into SQL
- Password verification via bcrypt (binary data, not SQL)

#### Test 6: Token Replay Attack
```bash
# Capture valid token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use same token multiple times
for i in {1..5}; do
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/employees
done

# Revoke token
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Try to reuse after revocation
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/employees
```

**Expected Result:**
- Token works for multiple legitimate requests
- After logout, token is revoked and returns 401
- Revocation verified against database on each request

**Protection Mechanism:**
- JTI (JWT ID) stored in database
- Token lookup checks revoked status
- Immediate revocation on logout

#### Test 7: Brute-Force Attack Detection
```bash
# Simulate brute-force with 10 failed login attempts
for i in {1..10}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"attacker@example.com\",
      \"password\": \"WrongPassword$i\"
    }"
done

# Check logs for brute-force pattern
SELECT source_ip, COUNT(*) as attempts
FROM auth_logs
WHERE action = 'login' AND result = 'failure'
GROUP BY source_ip;
```

**Expected Result:**
- 10 failed login attempts logged with attacker's IP
- Each attempt returns 401 Unauthorized
- No account lockout (implement at business logic level if needed)

**Mitigation Strategy:**
- Monitor logs for >5 failures in 15 minutes per IP
- Implement rate limiting at API Gateway or WAF level
- Alert on suspicious patterns

#### Test 8: Broken Access Control (IDOR)
```bash
# Employee 1 tries to access Employee 2's data
EMP1_TOKEN=$(login "emp1@example.com")

# Try to access different employee's profile
curl -H "Authorization: Bearer $EMP1_TOKEN" \
  http://localhost:8000/employees/2

# Try to modify different employee
curl -X PUT -H "Authorization: Bearer $EMP1_TOKEN" \
  -d '{"name": "Hacked"}' \
  http://localhost:8000/employees/2
```

**Expected Result:**
- GET returns 403 Forbidden if not own record
- PUT returns 403 Forbidden
- Attempts logged as "403" with user/endpoint/resource info

**Protection Mechanism:**
- `require_self_or_roles()` dependency checks:
  1. User is Admin (bypass all checks)
  2. User role in allowed_roles list
  3. Resource ID matches user's own ID
- Audit log includes denied attempts for investigation

#### Test 9: Invalid Token Rejection
```bash
# Malformed token (tampered JWT)
curl -H "Authorization: Bearer malformed.token.here" \
  http://localhost:8000/employees

# Expired token
OLD_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # from >45 min ago
curl -H "Authorization: Bearer $OLD_TOKEN" \
  http://localhost:8000/employees

# Missing Authorization header
curl http://localhost:8000/employees
```

**Expected Results:**
- Malformed token: 401 Unauthorized ("Invalid or expired token")
- Expired token: 401 Unauthorized (JWT lib raises ExpiredSignatureError)
- Missing header: 401 Unauthorized ("Missing Authorization header")
- All attempts logged as "401" in audit logs

#### Test 10: Password Strength Validation
```bash
# Weak passwords
WEAK_PASSWORDS=(
  '123456'              # No uppercase, no special char
  'Password'            # No number, no special char
  'pass123!'            # No uppercase
  'PASS123!'            # No lowercase
)

for pwd in "${WEAK_PASSWORDS[@]}"; do
  curl -X POST http://localhost:8000/auth/register \
    -d "{
      \"username\": \"user_$(date +%s)@example.com\",
      \"password\": \"$pwd\"
    }"
done

# Strong password
curl -X POST http://localhost:8000/auth/register \
  -d '{
    "username": "validuser@example.com",
    "password": "ValidPass123!"
  }'
```

**Expected Results:**
- Weak passwords: 400 Bad Request with validation error message
- Strong password: 201 Created, user successfully registered

### Running Automated Tests

```powershell
# Run all auth tests
pytest backend/tests/test_auth_flow.py -v

# Run with coverage
pytest backend/tests/test_auth_flow.py --cov=backend.controllers.auth --cov-report=html

# Run specific test
pytest backend/tests/test_auth_flow.py::test_login_success -v
```

### Manual Testing Checklist

- [ ] Register new user with all required fields
- [ ] Login with correct password
- [ ] Login with incorrect password (fails)
- [ ] Login with non-existent user (fails)
- [ ] Use token to access protected endpoint
- [ ] Logout revokes token
- [ ] Revoked token cannot access endpoints
- [ ] Refresh token issues new token
- [ ] Old token revoked after refresh
- [ ] Employee cannot access admin endpoints
- [ ] Employee can access own profile
- [ ] Employee cannot access other employee's profile
- [ ] Audit logs created for all actions
- [ ] Plaintext passwords never appear in logs
- [ ] Failed logins logged with source IP

---

## Token Management

### Token Lifecycle

```
1. CREATE: User logs in successfully
   └─ JWT token generated with HS256
   └─ JTI (unique ID) created
   └─ Token stored in auth_tokens table with expires_at

2. VALIDATE: User makes API request
   └─ Token extracted from Authorization header
   └─ JWT signature verified with secret key
   └─ Expiration time checked
   └─ JTI looked up in database
   └─ Revoked flag checked (revoked=false)

3. REFRESH: User calls /auth/refresh
   └─ Current token validated (not revoked, not expired)
   └─ Old token marked as revoked in database
   └─ New token generated with fresh expiration
   └─ Old JTI now returns 401 if reused

4. REVOKE: User logs out
   └─ JTI marked as revoked=true in database
   └─ Token still valid JWT, but rejected due to revocation flag
   └─ Any subsequent request with this token returns 401
```

### Token Structure

```json
{
  "sub": "1",                        // User ID (subject)
  "jti": "550e8400-e29b-41d4-a716-446655440000",  // JWT ID (for revocation)
  "iat": 1699564800,                 // Issued at (unix timestamp)
  "exp": 1699567600,                 // Expires at (unix timestamp) - 45 min later
  "role": "Employee",                // User role
  "username": "john@example.com"     // Username (for logging)
}
```

### Token Expiration Policy

- **Default Expiration**: 45 minutes
- **Configurable**: via `AUTH_JWT_EXP_MINUTES` env variable (30-60 min recommended)
- **Mechanism**: Unix timestamp in `exp` claim
- **Validation**: Server checks `exp` vs current time on every request

### Token Refresh Strategy

**Recommended Usage Pattern (Frontend):**
```javascript
// 1. User logs in
const response = await fetch('/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});
let token = response.json().access_token;

// 2. Store in memory (not localStorage)
let authToken = token;

// 3. Use token for API requests
const result = await fetch('/employees', {
  headers: { 'Authorization': `Bearer ${authToken}` }
});

// 4. If 401 Unauthorized received
if (response.status === 401) {
  // Try to refresh
  const refreshResponse = await fetch('/auth/refresh', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${authToken}` }
  });
  
  if (refreshResponse.ok) {
    authToken = refreshResponse.json().access_token;
    // Retry original request
  } else {
    // Redirect to login
  }
}
```

---

## Troubleshooting

### Common Issues

#### Issue: "Invalid credentials" on login
**Causes:**
- User doesn't exist
- Password is incorrect
- Username typo

**Solution:**
1. Verify user exists: `SELECT * FROM auth_users WHERE username = 'test@example.com';`
2. Reset password if needed: admin can create new account
3. Check logs for username attempts: `SELECT * FROM auth_logs WHERE action='login' AND result='failure' ORDER BY timestamp DESC;`

---

#### Issue: Token immediately expires
**Causes:**
- `AUTH_JWT_EXP_MINUTES` set too low
- System clock skew between client and server
- Token generated with wrong secret

**Solution:**
1. Check env: `grep AUTH_JWT_EXP_MINUTES backend/.env`
2. Ensure server time is synchronized: `date` (should be UTC)
3. Verify JWT secret unchanged: `echo $AUTH_JWT_SECRET`

---

#### Issue: "Token revoked" error despite recent login
**Causes:**
- User logged out (token revoked)
- Token refresh issued (old token revoked)
- Database cleared

**Solution:**
1. User must login again to get new token
2. Check audit logs: `SELECT * FROM auth_logs WHERE user_id=123 ORDER BY timestamp DESC;`
3. Verify database not reset

---

#### Issue: "Forbidden" (403) accessing allowed endpoint
**Causes:**
- User role doesn't have permission
- Trying to access other user's data (Employee)
- IDOR protection preventing access

**Solution:**
1. Check user's role: `SELECT role FROM auth_users WHERE id=123;`
2. Compare against endpoint requirements (see Access Control Matrix)
3. For Employee, verify accessing own record ID
4. Admin can access everything

---

#### Issue: Password hash not saving or validation fails
**Causes:**
- Bcrypt library not installed
- Password column too short (string length)
- Hash function not called

**Solution:**
```bash
# Verify dependencies
pip list | grep bcrypt
# Should show: passlib[bcrypt]

# Check database column size
SELECT CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME='auth_users' AND COLUMN_NAME='password_hash';
# Should be >= 512 characters

# Verify hash function used in code
grep -n "hash_password" backend/controllers/auth.py
```

---

### Debugging Tips

**Enable detailed logging:**
```python
# In backend/utils/logger.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set ENV
export LOGLEVEL=DEBUG
```

**Check JWT token contents:**
```python
import jwt
import os

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
secret = os.getenv("AUTH_JWT_SECRET")

try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    print("Token valid:")
    print(f"  User ID: {payload['sub']}")
    print(f"  Role: {payload['role']}")
    print(f"  Expires: {payload['exp']}")
except jwt.ExpiredSignatureError:
    print("Token expired")
except Exception as e:
    print(f"Token invalid: {e}")
```

**Query audit logs:**
```sql
-- Recent auth events
SELECT timestamp, username, action, result, source_ip
FROM auth_logs
ORDER BY timestamp DESC
LIMIT 20;

-- Failed logins by user
SELECT username, COUNT(*) as attempts
FROM auth_logs
WHERE action='login' AND result='failure'
  AND timestamp > NOW() - INTERVAL 1 HOUR
GROUP BY username;

-- All events for specific user
SELECT * FROM auth_logs
WHERE user_id = 123
ORDER BY timestamp DESC;
```

---

## Implementation Checklist

- [x] JWT authentication implemented with HS256
- [x] Bcrypt password hashing with salt
- [x] User registration endpoint
- [x] Login endpoint with token issuance
- [x] Logout endpoint with token revocation
- [x] Token refresh endpoint
- [x] RBAC with 4 roles (Admin, HR Manager, Payroll Manager, Employee)
- [x] Role-based endpoint protection
- [x] Audit logging to AUTH_DB.Logs
- [x] Token expiration (45 minutes)
- [x] JTI tracking for revocation
- [x] Password complexity validation
- [x] SQL injection protection
- [x] IDOR protection (self/role checks)
- [x] Brute-force attack logging
- [x] Environment variable configuration
- [ ] Rate limiting (implement at API Gateway/WAF)
- [ ] HTTPS/TLS 1.3 deployment (production)
- [ ] 90-day log retention policy (implement in deployment)
- [ ] Security test suite (expand as needed)

---

## Additional Resources

- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Bcrypt Algorithm](https://en.wikipedia.org/wiki/Bcrypt)

---

**Last Updated**: 2025-04-22
**Maintained By**: Development Team
**Security Review**: Quarterly or after security incidents

