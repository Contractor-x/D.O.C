from typing import Optional
from datetime import datetime

def format_medication_name(name: str) -> str:
    """Format medication name for display."""
    return name.title()

def format_dosage(dosage: str) -> str:
    """Format dosage string."""
    return dosage.strip().lower()

def format_side_effect_name(name: str) -> str:
    """Format side effect name."""
    return name.lower().strip()

def format_datetime_display(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%B %d, %Y at %I:%M %p")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return ".1f"
        size_bytes /= 1024.0
    return ".1f"
