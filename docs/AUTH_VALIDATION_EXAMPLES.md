"""
DEMO: User Authentication & Data Validation Examples

This file shows examples of how to use the validation system
in both backend and frontend contexts.
"""

# ============================================================================
# BACKEND EXAMPLES - Python/FastAPI
# ============================================================================

# Example 1: Using validators directly
# ============================================================================
from backend.utils.validators import validate_password, validate_username

# Validate a password
password = "MySecurePass123!"
is_valid, error_msg = validate_password(password)
if is_valid:
    print("✓ Password is strong")
else:
    print(f"✗ Password validation failed: {error_msg}")

# Validate a username
username = "john_doe"
is_valid, error_msg = validate_username(username)
if is_valid:
    print("✓ Username format is valid")
else:
    print(f"✗ Username validation failed: {error_msg}")


# Example 2: Using in FastAPI endpoint
# ============================================================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from backend.utils.validators import validate_password

router = APIRouter()

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        is_valid, error = validate_password(v)
        if not is_valid:
            raise ValueError(error)
        return v

@router.post("/user/change-password")
def change_password(req: PasswordChangeRequest):
    """
    When this endpoint is called:
    1. Pydantic validates the model
    2. Field validators run automatically
    3. If validation fails, 422 response is returned
    4. If validation passes, the function is called
    """
    # At this point, we know req.new_password is strong
    # because Pydantic validation passed
    return {"status": "password changed"}


# Example 3: Handling validation errors
# ============================================================================
from backend.utils.validators import validate_login_input

def process_login(username: str, password: str):
    # Validate input
    is_valid, error_msg = validate_login_input(username, password)
    if not is_valid:
        # Return 400 Bad Request with error details
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Continue with actual authentication
    # ... find user in database ...
    # ... verify password ...
    # ... create token ...


# Example 4: Batch validation (multiple fields)
# ============================================================================
from backend.utils.validators import (
    validate_username, validate_password, validate_email, validate_role
)

def validate_registration_form(data: dict) -> dict:
    """
    Validate all fields in registration form
    Returns dict with validation results
    """
    errors = {}
    
    # Validate each field
    username_valid, username_error = validate_username(data.get('username', ''))
    if not username_valid:
        errors['username'] = username_error
    
    password_valid, password_error = validate_password(data.get('password', ''))
    if not password_valid:
        errors['password'] = password_error
    
    email_valid, email_error = validate_email(data.get('email', ''))
    if not email_valid:
        errors['email'] = email_error
    
    role_valid, role_error = validate_role(data.get('role', ''))
    if not role_valid:
        errors['role'] = role_error
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

# Usage
result = validate_registration_form({
    'username': 'john_doe',
    'password': 'weak',
    'email': 'john@example.com',
    'role': 'Employee'
})

if result['is_valid']:
    print("✓ All fields valid")
else:
    print("✗ Validation errors:")
    for field, error in result['errors'].items():
        print(f"  - {field}: {error}")


# ============================================================================
# FRONTEND EXAMPLES - JavaScript/React
# ============================================================================

// Example 1: Using validators in React component
// ============================================================================
import { validatePassword, getPasswordStrength } from '../utils/validators';
import { useState } from 'react';

function PasswordInput() {
  const [password, setPassword] = useState('');
  const [strength, setStrength] = useState(0);
  const [error, setError] = useState('');
  
  const handleChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    
    // Real-time validation
    const validation = validatePassword(value);
    setError(validation.error);
    
    // Update strength
    setStrength(getPasswordStrength(value));
  };
  
  return (
    <div>
      <input 
        type="password"
        value={password}
        onChange={handleChange}
        placeholder="Enter password"
      />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {password && <p>Strength: {strength}/4</p>}
    </div>
  );
}


// Example 2: Form validation with multiple fields
// ============================================================================
import { validateUsername, validatePassword, validateEmail } from '../utils/validators';

function RegistrationForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  
  const [errors, setErrors] = useState({});
  
  const validateField = (field, value) => {
    let validation;
    
    switch(field) {
      case 'username':
        validation = validateUsername(value);
        break;
      case 'email':
        validation = validateEmail(value);
        break;
      case 'password':
        validation = validatePassword(value);
        break;
      default:
        return true;
    }
    
    if (!validation.valid) {
      setErrors(prev => ({ ...prev, [field]: validation.error }));
      return false;
    } else {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
      return true;
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    validateField(name, value);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate all fields
    let isValid = true;
    isValid &= validateField('username', formData.username);
    isValid &= validateField('email', formData.email);
    isValid &= validateField('password', formData.password);
    
    if (isValid) {
      // Submit form
      console.log('Submitting:', formData);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          name="username"
          value={formData.username}
          onChange={handleChange}
        />
        {errors.username && <p className="error">{errors.username}</p>}
      </div>
      
      <div>
        <input
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
        />
        {errors.email && <p className="error">{errors.email}</p>}
      </div>
      
      <div>
        <input
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
        />
        {errors.password && <p className="error">{errors.password}</p>}
      </div>
      
      <button type="submit" disabled={Object.keys(errors).length > 0}>
        Register
      </button>
    </form>
  );
}


// Example 3: API error handling with validation
// ============================================================================
import axios from 'axios';
import { validateLoginForm } from '../utils/validators';

async function loginUser(username, password) {
  // Client-side validation
  const validation = validateLoginForm(username, password);
  if (!validation.valid) {
    return { error: validation.error };
  }
  
  try {
    // Make API request
    const response = await axios.post('/auth/login', {
      username,
      password
    });
    
    return { success: true, data: response.data };
  } catch (error) {
    // Handle API validation errors
    if (error.response?.status === 400) {
      // Server-side validation failed
      return { error: error.response.data.detail };
    } else if (error.response?.status === 401) {
      // Authentication failed
      return { error: 'Invalid username or password' };
    } else {
      // Other errors
      return { error: 'An error occurred. Please try again.' };
    }
  }
}

// Usage
const result = await loginUser('user@example.com', 'password123');
if (result.error) {
  console.error('Login failed:', result.error);
} else {
  console.log('Login successful:', result.data);
}


// Example 4: Real-time password strength indicator
// ============================================================================
import { useState } from 'react';
import { getPasswordStrength, getPasswordStrengthLabel } from '../utils/validators';

function PasswordStrengthIndicator() {
  const [password, setPassword] = useState('');
  const strength = getPasswordStrength(password);
  const label = getPasswordStrengthLabel(strength);
  
  const strengthColors = ['#d32f2f', '#f57c00', '#fbc02d', '#388e3c'];
  const color = strengthColors[strength - 1] || '#ccc';
  
  return (
    <div>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Enter password"
      />
      {password && (
        <div>
          <div
            style={{
              height: '4px',
              backgroundColor: '#e0e0e0',
              borderRadius: '2px',
              overflow: 'hidden'
            }}
          >
            <div
              style={{
                width: `${(strength / 4) * 100}%`,
                height: '100%',
                backgroundColor: color,
                transition: 'width 0.3s ease'
              }}
            />
          </div>
          <p style={{ color }}>Strength: {label}</p>
        </div>
      )}
    </div>
  );
}


// ============================================================================
// INTEGRATION EXAMPLES
// ============================================================================

// Example: Full login flow with validation
// ============================================================================

// Backend - enhanced login endpoint
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator
from backend.utils.validators import validate_login_input

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str
    
    @field_validator('username', 'password')
    def validate_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

@router.post("/auth/login")
def login(req: LoginRequest, request: Request):
    """
    Complete login with validation:
    1. Pydantic validates basic constraints
    2. Field validators ensure non-empty
    3. validate_login_input checks lengths
    4. Password verification performed
    5. Token created and returned
    """
    db = SessionAuth()
    try:
        # Additional validation
        is_valid, error = validate_login_input(req.username, req.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Find user and verify password
        user = db.query(AuthUser).filter(
            AuthUser.username == req.username
        ).one_or_none()
        
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_access_token(subject=str(user.id))
        
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.close()


// Frontend - login with validation
import { useState } from 'react';
import { validateLoginForm } from '../utils/validators';
import { login } from '../services/auth';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Client-side validation
    const validation = validateLoginForm(username, password);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }
    
    // Submit to server
    setLoading(true);
    try {
      await login(username, password);
      // Redirect to dashboard
    } catch (err) {
      // Handle server validation errors
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username or email"
        disabled={loading}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        disabled={loading}
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
