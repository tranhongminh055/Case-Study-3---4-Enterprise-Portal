# User Authentication Validation - Quick Reference

## Password Requirements

✓ **Must have:**
- Minimum 8 characters
- At least 1 UPPERCASE letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 digit (0-9)
- At least 1 special character (!@#$%^&*)

✗ **Example of weak password:** `password123` (no special char, no uppercase)
✓ **Example of strong password:** `MyPassword123!`

## Username Requirements

✓ **Must have:**
- 3-50 characters long
- Only letters, numbers, dots (.), hyphens (-), or underscores (_)

✗ **Invalid:** `user@name`, `user name`, `ab`
✓ **Valid:** `john_doe`, `user.name`, `test-123`, `MyUser`

## Email/Login Requirements

✓ **Must have:**
- Valid email format
- Maximum 255 characters

✗ **Invalid:** `notanemail`, `user@`, `@example.com`
✓ **Valid:** `user@example.com`, `john.doe@company.com`

## Role Options

- Employee
- HR Manager
- Payroll Manager
- Admin

## API Endpoints

### POST /auth/login
**Request:**
```json
{
  "username": "user@example.com",
  "password": "MyPassword123!"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "Employee"
}
```

**Error Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

### POST /auth/register
**Request:**
```json
{
  "username": "newuser",
  "password": "MyPassword123!",
  "role": "Employee"
}
```

**Success Response (201):**
```json
{
  "id": 1,
  "username": "newuser",
  "role": "Employee"
}
```

**Error Response (400):**
```json
{
  "detail": "Password must contain: at least one uppercase letter, ..."
}
```

## Error Codes

| Code | Meaning | Typical Cause |
|------|---------|---------------|
| 400  | Bad Request | Validation error (invalid format/strength) |
| 401  | Unauthorized | Invalid username/password |
| 409  | Conflict | Username already exists |
| 500  | Server Error | Unexpected error |

## Common Validation Errors

### Password Validation
- "Password must contain: at least 8 characters" → password too short
- "Password must contain: at least one uppercase letter" → add A-Z
- "Password must contain: at least one lowercase letter" → add a-z
- "Password must contain: at least one digit" → add 0-9
- "Password must contain: at least one special character" → add !@#$%^&*()

### Username Validation
- "Username must be at least 3 characters" → too short
- "Username must not exceed 50 characters" → too long
- "Username can only contain letters, numbers, dots, hyphens, and underscores" → invalid character

### Email Validation
- "Invalid email format" → missing @ or domain
- "Email is too long (max 255 characters)" → extremely long email

### Role Validation
- "Invalid role. Must be one of: Employee, HR Manager, Payroll Manager, Admin" → invalid role

## Frontend Features

### Real-Time Validation
- Errors appear as you type
- Errors disappear when you fix the problem

### Password Strength Indicator
- **Red** = Weak (missing most requirements)
- **Orange** = Fair (missing some requirements)
- **Yellow** = Good (meeting most requirements)
- **Green** = Strong (all requirements met)

### Field-Level Errors
- Each field shows its own error message
- Form is disabled while submitting
- Loading state prevents accidental double-submit

## Testing Locally

### Test Valid Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"Test123@Password"}'
```

### Test Invalid Password Strength
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"weak","role":"Employee"}'
```

Response: `{"detail":"Password must contain: at least 8 characters, at least one uppercase letter, ..."}`

### Test Duplicate Username
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"existinguser","password":"Test123@Password","role":"Employee"}'
```

Response: `{"detail":"Username already exists"}` (409 Conflict)

## Key Files

### Backend
- `backend/utils/validators.py` - Core validation logic
- `backend/controllers/auth.py` - API endpoints with Pydantic validation
- `backend/tests/test_auth_validation.py` - Test suite

### Frontend
- `frontend/src/utils/validators.js` - Client-side validation
- `frontend/src/components/LoginForm.jsx` - Login with validation
- `frontend/src/components/RegisterForm.jsx` - Registration with strength indicator
- `frontend/src/index.css` - Validation UI styles

## Security Best Practices

1. **Always validate server-side** - Never trust client-side validation alone
2. **Never log passwords** - Passwords are hashed and never displayed
3. **Use HTTPS in production** - Encrypt credentials in transit
4. **Update JWT_SECRET** - Change default secret in production
5. **Rate limiting** - Implement rate limiting on auth endpoints
6. **Monitor failed attempts** - Track suspicious login patterns

## Integration Checklist

- [ ] Backend validators imported in auth controller
- [ ] Pydantic models configured with field validators
- [ ] Frontend validators imported in form components
- [ ] LoginForm and RegisterForm updated with validation
- [ ] CSS styles added to index.css
- [ ] Test file created and tests passing
- [ ] Documentation updated
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] Error handling tested
