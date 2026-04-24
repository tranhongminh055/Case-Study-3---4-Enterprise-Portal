import re
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format.
    
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip()
    
    # Email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long (max 255 characters)"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    errors = []
    
    if len(password) < 8:
        errors.append("at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("at least one digit")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("at least one special character")
    
    if errors:
        return False, "Password must contain: " + ", ".join(errors)
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format.
    
    Requirements:
    - 3-50 characters
    - Only letters, numbers, dots, hyphens, underscores
    
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    
    pattern = r'^[a-zA-Z0-9._-]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"
    
    return True, ""


def validate_role(role: str) -> Tuple[bool, str]:
    """Validate user role.
    
    Returns: (is_valid, error_message)
    """
    if not role:
        return False, "Role is required"
    
    valid_roles = ['Employee', 'HR Manager', 'Payroll Manager', 'Admin']
    if role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    
    return True, ""


def validate_login_input(username: str, password: str) -> Tuple[bool, str]:
    """Validate login form inputs.
    
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Email/Username is required"
    
    if not password:
        return False, "Password is required"
    
    if len(username) > 255:
        return False, "Email/Username is too long"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    return True, ""
