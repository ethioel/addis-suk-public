# src/utils/__init__.py
# Utility functions for Addis Suk Bot

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import re


def format_price(price: float, currency: str = "Br") -> str:
    """Format price with Ethiopian Birr symbol."""
    if price >= 1000:
        return f"{price:,.0f} {currency}"
    return f"{price:.2f} {currency}"


def format_distance(km: float) -> str:
    """Format distance for display."""
    if km < 1:
        return f"{int(km * 1000)}m"
    return f"{km:.1f}km"


def validate_phone_number(phone: str) -> bool:
    """Validate Ethiopian phone number."""
    # Ethiopian phone: 09XX XXX XXX or +2519XX XXX XXX
    pattern = r'^(\+?251|0)9\d{8}$'
    return bool(re.match(pattern, phone.replace(" ", "")))


def normalize_phone(phone: str) -> str:
    """Normalize phone number to standard Ethiopian format."""
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("+251"):
        phone = "0" + phone[4:]
    elif phone.startswith("251"):
        phone = "0" + phone[3:]
    return phone


def format_datetime(dt: datetime, lang: str = 'en') -> str:
    """Format datetime for display."""
    if lang == 'am':
        months_am = [
            "ጃንዩወሪ", "ፌብሩወሪ", "ማርች", "ኤንውሪ", "ሜይ", "ጁን",
            "ጁላይ", "ኦገስት", "ሴፖተምበር", "ኦክቶበር", "ኖቬምበር", "ዲሴምበር"
        ]
        return f"{dt.day} {months_am[dt.month - 1]} {dt.year}"
    else:
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return f"{months[dt.month - 1]} {dt.day}, {dt.year}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def escape_markdown(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    
    diff = datetime.utcnow() - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        return format_datetime(dt)


def generate_receipt_reference() -> str:
    """Generate a unique receipt reference."""
    import uuid
    return f"TXN{uuid.uuid4().hex[:8].upper()}"


# Re-export commonly used utilities
__all__ = [
    "format_price",
    "format_distance",
    "validate_phone_number",
    "normalize_phone",
    "format_datetime",
    "truncate_text",
    "escape_markdown",
    "get_time_ago",
    "generate_receipt_reference",
]