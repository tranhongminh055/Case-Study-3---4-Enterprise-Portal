"""
Test suite for user authentication and data validation
Run with: python -m pytest backend/tests/test_auth_validation.py -v
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils.validators import (
    validate_email, validate_password, validate_username, 
    validate_role, validate_login_input
)

client = TestClient(app)


class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_empty_password(self):
        is_valid, error = validate_password("")
        assert not is_valid
        assert "required" in error.lower()
    
    def test_password_too_short(self):
        is_valid, error = validate_password("Short1!")
        assert not is_valid
        assert "8 characters" in error
    
    def test_password_missing_uppercase(self):
        is_valid, error = validate_password("secure1!")
        assert not is_valid
        assert "uppercase" in error
    
    def test_password_missing_lowercase(self):
        is_valid, error = validate_password("SECURE1!")
        assert not is_valid
        assert "lowercase" in error
    
    def test_password_missing_digit(self):
        is_valid, error = validate_password("Secure!")
        assert not is_valid
        assert "digit" in error
    
    def test_password_missing_special_char(self):
        is_valid, error = validate_password("Secure1")
        assert not is_valid
        assert "special character" in error
    
    def test_password_too_long(self):
        long_pwd = "A" * 200 + "a1!"
        is_valid, error = validate_password(long_pwd)
        assert not is_valid
        assert "too long" in error
    
    def test_valid_password(self):
        is_valid, error = validate_password("SecurePass123!")
        assert is_valid
        assert error == ""
    
    def test_valid_password_with_various_special_chars(self):
        valid_passwords = [
            "SecurePass123!",
            "MyPass@2024",
            "Test#Pass123",
            "Valid$Pwd456",
        ]
        for pwd in valid_passwords:
            is_valid, error = validate_password(pwd)
            assert is_valid, f"Password '{pwd}' should be valid: {error}"


class TestUsernameValidation:
    """Test username format validation"""
    
    def test_empty_username(self):
        is_valid, error = validate_username("")
        assert not is_valid
        assert "required" in error.lower()
    
    def test_username_too_short(self):
        is_valid, error = validate_username("ab")
        assert not is_valid
        assert "3 characters" in error
    
    def test_username_too_long(self):
        long_user = "a" * 51
        is_valid, error = validate_username(long_user)
        assert not is_valid
        assert "exceed 50" in error
    
    def test_username_with_invalid_chars(self):
        invalid_usernames = [
            "user@name",
            "user name",
            "user#name",
            "user!name",
        ]
        for username in invalid_usernames:
            is_valid, error = validate_username(username)
            assert not is_valid, f"Username '{username}' should be invalid"
    
    def test_valid_username(self):
        valid_usernames = [
            "john_doe",
            "user.name",
            "user-123",
            "TestUser",
            "test_user_123",
        ]
        for username in valid_usernames:
            is_valid, error = validate_username(username)
            assert is_valid, f"Username '{username}' should be valid: {error}"


class TestEmailValidation:
    """Test email format validation"""
    
    def test_empty_email(self):
        is_valid, error = validate_email("")
        assert not is_valid
        assert "required" in error.lower()
    
    def test_invalid_email_format(self):
        invalid_emails = [
            "notanemail",
            "user@",
            "@example.com",
            "user@.com",
            "user name@example.com",
        ]
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert not is_valid, f"Email '{email}' should be invalid"
    
    def test_valid_email(self):
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test+tag@example.com",
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid, f"Email '{email}' should be valid: {error}"


class TestRoleValidation:
    """Test role validation"""
    
    def test_empty_role(self):
        is_valid, error = validate_role("")
        assert not is_valid
    
    def test_invalid_role(self):
        is_valid, error = validate_role("InvalidRole")
        assert not is_valid
        assert "Invalid role" in error
    
    def test_valid_roles(self):
        valid_roles = ["Employee", "HR Manager", "Payroll Manager", "Admin"]
        for role in valid_roles:
            is_valid, error = validate_role(role)
            assert is_valid, f"Role '{role}' should be valid: {error}"


class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    def test_login_missing_username(self):
        response = client.post("/auth/login", json={
            "password": "SecurePass123!"
        })
        assert response.status_code in [400, 422]
    
    def test_login_missing_password(self):
        response = client.post("/auth/login", json={
            "username": "user@example.com"
        })
        assert response.status_code in [400, 422]
    
    def test_register_weak_password(self):
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "weak",
            "role": "Employee"
        })
        assert response.status_code == 400
        assert "password" in response.json().get("detail", "").lower()
    
    def test_register_invalid_username(self):
        response = client.post("/auth/register", json={
            "username": "ab",  # Too short
            "password": "SecurePass123!",
            "role": "Employee"
        })
        assert response.status_code == 400
        assert "username" in response.json().get("detail", "").lower()
    
    def test_register_invalid_role(self):
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "SecurePass123!",
            "role": "InvalidRole"
        })
        assert response.status_code == 400
        assert "role" in response.json().get("detail", "").lower()
    
    def test_login_nonexistent_user(self):
        response = client.post("/auth/login", json={
            "username": "nonexistent@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json().get("detail", "")


class TestPasswordStrengthIndicator:
    """Test password strength scoring"""
    
    def test_password_strength_scoring(self):
        # This test would be frontend-specific
        # Documenting the expected scoring:
        # 0-1 strength: Weak
        # 2 strength: Fair
        # 3 strength: Good
        # 4 strength: Strong
        pass


class TestFormValidation:
    """Test combined form validation"""
    
    def test_login_form_both_empty(self):
        is_valid, error = validate_login_input("", "")
        assert not is_valid
        assert "required" in error.lower()
    
    def test_login_form_valid(self):
        is_valid, error = validate_login_input("user@example.com", "ValidPass1!")
        assert is_valid
        assert error == ""
    
    def test_register_complete_flow(self):
        """Test a complete registration workflow"""
        # This would be an integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
