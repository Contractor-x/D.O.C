import pytest
from ..app.services.auth_service import AuthService
from ..app.schemas.user import UserCreate

def test_create_user(db):
    user_data = UserCreate(email="test@example.com", password="password123", full_name="Test User")
    user = AuthService.create_user(db, user_data)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.hashed_password != "password123"  # Should be hashed

def test_authenticate_user(db):
    # Create user first
    user_data = UserCreate(email="auth@example.com", password="password123")
    AuthService.create_user(db, user_data)

    # Test authentication
    user = AuthService.authenticate_user(db, "auth@example.com", "password123")
    assert user is not None
    assert user.email == "auth@example.com"

def test_authenticate_invalid_user(db):
    user = AuthService.authenticate_user(db, "nonexistent@example.com", "password")
    assert user is False
