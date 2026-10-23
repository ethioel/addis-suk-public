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
        """Test that the full default taxonomy is seeded."""
        categories = await db.fetchall(
            "SELECT name_en FROM categories ORDER BY display_order"
        )
        names = {r['name_en'] for r in categories}
        assert len(names) >= 10
        for expected in ("Vegetables", "Fruits", "Meat & Poultry", "Dairy & Eggs",
                         "Grains & Pulses", "Spices & Oil", "Bakery & Injera",
                         "Coffee, Tea & Drinks", "Snacks & Sweets", "Household & Care"):
            assert expected in names

    async def test_category_amharic_labels_fixed(self, db):
        """Regression: old garbled Amharic labels must be refreshed on init."""
        veg = await db.fetchone(
            "SELECT name_am FROM categories WHERE name_en = 'Vegetables'"
        )
        assert veg['name_am'] == "አትክልቶች"

    async def test_category_migration_preserves_ids(self, db):
        """Old taxonomies migrate by rename so item category ids stay valid."""
        # Simulate a database seeded with the old taxonomy
        await db.execute("DELETE FROM categories")
        old = [
            ("Vegetables", "የአቲካል ወተት", "🥦", 0),
            ("Meat", "ሥጋ", "🥩", 2),
            ("Household", "የቤት ሰረዝ", "🧴", 6),
        ]
        for name, am, emoji, order in old:
            await db.execute(
                "INSERT INTO categories (name_en, name_am, emoji, display_order) "
                "VALUES (?, ?, ?, ?)",
                (name, am, emoji, order)
            )
        meat_id = (await db.fetchone(
            "SELECT id FROM categories WHERE name_en = 'Meat'"
        ))['id']
        await db.execute(
            "INSERT INTO items (seller_id, category_id, name_en, name_am, price, unit, status) "
            "VALUES (1, ?, 'Beef', 'የበሬ ሥጋ', 220.0, 'kg', 'approved')",
            (meat_id,)
        )
        await db.execute(
            "INSERT INTO sellers (id, user_id, shop_name, address, phone, city, status) "
            "VALUES (1, 1, 'S', 'A', '09', 'Addis Ababa', 'approved')"
        )

        await db.init()  # re-run migration + seeding

        names = {r['name_en'] for r in await db.fetchall("SELECT name_en FROM categories")}
        assert "Meat & Poultry" in names
        assert "Household & Care" in names
        assert "Meat" not in names
        assert len(names) >= 10
        # The Beef item must still point at the renamed (same-id) category
        row = await db.fetchone(
            "SELECT c.name_en FROM items i JOIN categories c ON i.category_id = c.id "
            "WHERE i.name_en = 'Beef'"
        )
        assert row['name_en'] == "Meat & Poultry"
    
    async def test_indexes_exist(self, db):
        """Test that all required indexes exist."""
        indexes = await db.fetchall(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users'"
        )
        assert len(indexes) >= 1