"""Regression tests for search-by-input crash, favorites feedback and custom locations."""
import os
import pytest
from datetime import datetime

from src.models.database import Database
from src.middleware import UserMiddleware
from src.services import FavoriteService


@pytest.fixture
async def db():
    database = Database("data/test_regression.db")
    await database.init()
    yield database
    if os.path.exists("data/test_regression.db"):
        os.remove("data/test_regression.db")


@pytest.mark.asyncio
async def test_user_middleware_autocreates_missing_user(db):
    """Regression: typed search after DB wipe must not crash on user=None."""
    from aiogram.types import Message, Chat, User as TgUser

    message = Message.model_construct(
        message_id=1,
        date=datetime.now(),
        chat=Chat.model_construct(id=100, type="private"),
        from_user=TgUser.model_construct(id=4242, is_bot=False, first_name="Tester"),
        text="onion",
    )

    async def handler(event, data):
        return data['user']

    mw = UserMiddleware()
    data = {'db': db}
    user = await mw(handler, message, data)
    assert user is not None
    assert user['telegram_id'] == 4242
    assert user['first_name'] == "Tester"
    assert isinstance(user, dict) and 'id' in user


@pytest.mark.asyncio
async def test_add_favorite_returns_false_on_duplicate(db):
    await db.execute(
        "INSERT INTO users (telegram_id, first_name) VALUES (1, 'T')"
    )
    await db.execute(
        "INSERT INTO sellers (user_id, shop_name, address, phone, city, status) "
        "VALUES (1, 'S', 'A', '09', 'Adama', 'approved')"
    )
    await db.execute(
        "INSERT INTO items (seller_id, category_id, name_en, name_am, price, unit, status) "
        "VALUES (1, 1, 'Onion', 'ሽንኩርት', 7.5, 'kg', 'approved')"
    )
    item = await db.fetchone("SELECT id FROM items LIMIT 1")
    user = await db.fetchone("SELECT id FROM users LIMIT 1")
    svc = FavoriteService(db)
    assert await svc.add_favorite(user['id'], item['id']) is True
    assert await svc.add_favorite(user['id'], item['id']) is False


@pytest.mark.asyncio
async def test_custom_locations_table_and_merge(db):
    from src.bot import AddisSukBot

    await db.execute(
        "INSERT INTO custom_locations (name, name_am, latitude, longitude, is_subcity) "
        "VALUES ('Debre Markos', 'ደብረ ማርቆስ', 10.35, 37.72, 0)"
    )
    await db.execute(
        "INSERT INTO custom_locations (name, name_am, latitude, longitude, is_subcity) "
        "VALUES ('Gerji Mebrat', 'ገርጂ', 9.01, 38.83, 1)"
    )
    bot = AddisSukBot.__new__(AddisSukBot)
    cities = await bot._merged_cities(db)
    subs = await bot._merged_subcities(db)

    names = [c[0] for c in cities]
    assert "Addis Ababa" in names
    assert "Debre Markos" in names
    custom = cities[names.index("Debre Markos")]
    assert custom[1] == "ደብረ ማርቆስ"
    assert abs(custom[2] - 10.35) < 1e-6

    sub_names = [s[0] for s in subs]
    assert "Bole" in sub_names
    assert "Gerji Mebrat" in sub_names
