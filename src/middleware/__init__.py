from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from typing import Callable, Dict, Any, Awaitable
from src.config import config
from src.models.database import Database
from src.locales import i18n
import time


class DatabaseMiddleware(BaseMiddleware):

    def __init__(self, db: Database):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.db
        return await handler(event, data)


class LocalizationMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        lang = 'en'
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            db: Database = data.get('db')
            if db:
                user = await db.fetchone(
                    "SELECT language FROM users WHERE telegram_id = ?", (user_id,)
                )
                if user:
                    lang = user['language']
        data['i18n'] = i18n
        data['lang'] = lang
        data['t'] = lambda key: i18n.get(key, lang)
        return await handler(event, data)


class UserMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        data['user'] = None
        data['is_admin'] = False
        data['user_role'] = 'buyer'
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            db: Database = data.get('db')
            if db:
                user = await db.fetchone(
                    "SELECT * FROM users WHERE telegram_id = ?", (user_id,)
                )
                if user:
                    data['user'] = user
                    data['is_admin'] = user_id in (config.ADMIN_IDS if config else [])
                    data['user_role'] = user['role']
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[int, list] = {}

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            now = time.time()
            if user_id in self._requests:
                self._requests[user_id] = [
                    t for t in self._requests[user_id]
                    if now - t < self.window_seconds
                ]
            else:
                self._requests[user_id] = []

            if len(self._requests[user_id]) >= self.max_requests:
                if isinstance(event, Message):
                    await event.answer("Too many requests. Please wait.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Too many requests.", show_alert=True)
                return
            self._requests[user_id].append(now)
        return await handler(event, data)


__all__ = [
    "DatabaseMiddleware",
    "LocalizationMiddleware",
    "UserMiddleware",
    "RateLimitMiddleware",
]