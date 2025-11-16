from typing import Optional
import re

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, None

def validate_phone(phone: str) -> bool:
    """Basic phone number validation."""
    pattern = r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    return re.match(pattern, phone) is not None

def validate_weight(weight: float) -> tuple[bool, Optional[str]]:
    """Validate weight in kg."""
    if weight <= 0:
        return False, "Weight must be positive"
    if weight > 500:
        return False, "Weight seems unrealistic"
    return True, None

def validate_age(age: int) -> tuple[bool, Optional[str]]:
    """Validate age in years."""
    if age < 0:
        return False, "Age cannot be negative"
    if age > 150:
        return False, "Age seems unrealistic"
    return True, None
