import re
from typing import Optional

def clean_string(text: str) -> str:
    """Clean and normalize string input."""
    return re.sub(r'\s+', ' ', text.strip())

def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_datetime(dt) -> str:
    """Format datetime to string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

def calculate_age(birth_date) -> Optional[int]:
    """Calculate age from birth date."""
    from datetime import date
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
