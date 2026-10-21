"""Tests for services."""
import pytest
from src.models.database import Database
from src.services import FavoriteService, AlertService


@pytest.fixture
async def services():
    """Create services with test database."""
    db = Database("data/test_services.db")
    await db.init()
    yield db
    import os
    if os.path.exists("data/test_services.db"):
        os.remove("data/test_services.db")


@pytest.mark.asyncio
class TestFavoriteService:
    
    async def test_add_favorite(self, services):
        """Test adding a favorite."""
        fav = FavoriteService(services)
        
        # Setup user and item
        await services.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
            (1, "TestUser")
        )
        user = await services.fetchone("SELECT id FROM users WHERE telegram_id = 1")
        await services.execute(
            "INSERT INTO items (seller_id, category_id, name_en, name_am, price, unit, status) VALUES (?, ?, ?, ?, ?, ?, 'approved')",
            (1, 1, "Tomato", "ቲማቲም", 80.0, "kg")
        )
        item = await services.fetchone("SELECT id FROM items WHERE name_en = 'Tomato'")
        
        result = await fav.add_favorite(user['id'], item['id'])
        assert result is True
    
    async def test_get_favorites(self, services):
        """Test getting user favorites."""
        fav = FavoriteService(services)
        
        await services.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
            (1, "TestUser")
        )
        await services.execute(
            "INSERT INTO sellers (user_id, shop_name, address, phone, city, status) VALUES (?, ?, ?, ?, ?, ?)",
            (1, "Test Shop", "Addr", "0912345678", "Addis", "approved")
        )
        await services.execute(
            "INSERT INTO items (seller_id, category_id, name_en, name_am, price, unit, status) VALUES (?, ?, ?, ?, ?, ?, 'approved')",
            (1, 1, "Tomato", "ቲማቲም", 80.0, "kg")
        )
        
        user = await services.fetchone("SELECT id FROM users WHERE telegram_id = 1")
        seller = await services.fetchone("SELECT id FROM sellers WHERE user_id = 1")
        item = await services.fetchone("SELECT id FROM items WHERE name_en = 'Tomato'")
        
        await fav.add_favorite(user['id'], item['id'])
        favorites = await fav.get_user_favorites(user['id'])
        assert len(favorites) >= 1


@pytest.mark.asyncio
class TestAlertService:
    
    async def test_create_alert(self, services):
        """Test creating a price alert."""
        alert_svc = AlertService(services)
        
        await services.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
            (1, "TestUser")
        )
        user = await services.fetchone("SELECT id FROM users WHERE telegram_id = 1")
        
        success, alert_id = await alert_svc.create_alert(
            user_id=user['id'],
            item_name="tomato",
            target_price=50.0
        )
        assert success is True
        assert alert_id > 0
    
    async def test_get_user_alerts(self, services):
        """Test getting user alerts."""
        alert_svc = AlertService(services)
        
        await services.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
            (1, "TestUser")
        )
        user = await services.fetchone("SELECT id FROM users WHERE telegram_id = 1")
        
        await alert_svc.create_alert(user_id=user['id'], item_name="tomato", target_price=50.0)
        alerts = await alert_svc.get_user_alerts(user['id'])
        assert len(alerts) >= 1