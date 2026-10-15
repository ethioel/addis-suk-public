"""Tests for database operations."""
import pytest
import aiosqlite
from src.models.database import Database
from src.config import config


@pytest.fixture
async def db():
    """Create test database."""
    test_db = Database("data/test.db")
    await test_db.init()
    yield test_db
    import os
    if os.path.exists("data/test.db"):
        os.remove("data/test.db")


@pytest.mark.asyncio
class TestDatabase:
    
    async def test_init_creates_database(self, db):
        """Test database initialization."""
        assert await db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    
    async def test_user_creation(self, db):
        """Test user creation."""
        result = await db.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
            (12345, "TestUser")
        )
        assert result.rowcount == 1
    
    async def test_seller_creation(self, db):
        """Test seller creation."""
        await db.execute(
            "INSERT INTO users (telegram_id, first_name, role) VALUES (?, ?, ?)",
            (12345, "Seller", "seller")
        )
        user = await db.fetchone("SELECT id FROM users WHERE telegram_id = 12345")
        await db.execute(
            "INSERT INTO sellers (user_id, shop_name, address, phone, city) VALUES (?, ?, ?, ?, ?)",
            (user['id'], "Test Shop", "Test Address", "0912345678", "Addis Ababa")
        )
        seller = await db.fetchone("SELECT id FROM sellers WHERE user_id = ?", (user['id'],))
        assert seller is not None
    
    async def test_category_seed(self, db):
        """Test that categories are seeded."""
        categories = await db.fetchall("SELECT * FROM categories")
        assert len(categories) >= 8
    
    async def test_indexes_exist(self, db):
        """Test that all required indexes exist."""
        indexes = await db.fetchall(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users'"
        )
        assert len(indexes) >= 1