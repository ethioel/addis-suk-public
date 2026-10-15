# src/filters/__init__.py
# Custom filters for Addis Suk Bot

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union, Dict, Any
from src.config import config


class IsAdmin(BaseFilter):
    """Check if user is an admin."""

    async def __call__(self, event: Union[Message, CallbackQuery], *args: Any) -> bool:
        return event.from_user.id in config.ADMIN_IDS


class IsRegisteredSeller(BaseFilter):
    """Check if user is a registered seller."""

    async def __call__(self, event: Union[Message, CallbackQuery], db=None, *args: Any) -> bool:
        if not db:
            return False
        seller = await db.fetchone(
            "SELECT status FROM sellers WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)",
            (event.from_user.id,)
        )
        return seller is not None and seller['status'] == 'approved'


class IsPremiumUser(BaseFilter):
    """Check if user is a premium subscriber."""

    async def __call__(self, event: Union[Message, CallbackQuery], db=None, *args: Any) -> bool:
        if not db:
            return False
        user = await db.fetchone(
            "SELECT subscription_tier, subscription_expires FROM users WHERE telegram_id = ?",
            (event.from_user.id,)
        )
        if not user:
            return False
        if user['subscription_tier'] != 'premium':
            return False
        if user['subscription_expires']:
            from datetime import datetime
            try:
                expires = datetime.fromisoformat(user['subscription_expires'])
                if expires > datetime.utcnow():
                    return True
            except (ValueError, TypeError):
                pass
        return False


class IsBuyer(BaseFilter):
    """Check if user is a buyer."""

    async def __call__(self, event: Union[Message, CallbackQuery], *args: Any) -> bool:
        return True  # Default to buyer


class HasLocation(BaseFilter):
    """Check if user has set a location."""

    async def __call__(self, event: Union[Message, CallbackQuery], db=None, *args: Any) -> bool:
        if not db:
            return False
        user = await db.fetchone(
            "SELECT latitude FROM users WHERE telegram_id = ?",
            (event.from_user.id,)
        )
        return user is not None and user['latitude'] is not None


class HasItem(BaseFilter):
    """Check if item exists in database."""

    def __init__(self, item_name: str):
        self.item_name = item_name.lower()

    async def __call__(self, event: Union[Message, CallbackQuery], db=None, *args: Any) -> bool:
        if not db:
            return False
        item = await db.fetchone(
            "SELECT id FROM items WHERE LOWER(name_en) = ? OR LOWER(name_am) = ?",
            (self.item_name, self.item_name)
        )
        return item is not None


class CallbackDataFilter(BaseFilter):
    """Filter callbacks by prefix."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.startswith(self.prefix) if callback.data else False