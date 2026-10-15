"""Tests for seller service."""
import pytest
from src.models.database import Database
from src.services import SellerService


@pytest.fixture
async def seller_service():
    """Create seller service with test database."""
    db = Database("data/test_seller.db")
    await db.init()
    yield SellerService(db)
    import os
    if os.path.exists("data/test_seller.db"):
        os.remove("data/test_seller.db")


@pytest.mark.asyncio
class TestSellerService:
    
    async def test_register_seller(self, seller_service):
        """Test seller registration."""
        success, seller_id = await seller_service.register_seller(
            user_id=1,
            shop_name="Test Shop",
            address="Test Address",
            phone="0912345678",
            city="Addis Ababa"
        )
        assert success is True
        assert seller_id > 0
    
    async def test_get_seller_by_user_id(self, seller_service):
        """Test retrieving seller by user ID."""
        await seller_service.register_seller(
            user_id=1, shop_name="Test Shop",
            address="Test Address", phone="0912345678", city="Addis Ababa"
        )
        seller = await seller_service.get_seller_by_user_id(1)
        assert seller is not None
        assert seller['shop_name'] == "Test Shop"
        assert seller['status'] == "pending"
    
    async def test_approve_seller(self, seller_service):
        """Test seller approval."""
        success, seller_id = await seller_service.register_seller(
            user_id=1, shop_name="Test Shop",
            address="Test Address", phone="0912345678", city="Addis Ababa"
        )
        assert await seller_service.approve_seller(seller_id)
        seller = await seller_service.get_seller_by_id(seller_id)
        assert seller['status'] == 'approved'
    
    async def test_reject_seller(self, seller_service):
        """Test seller rejection."""
        success, seller_id = await seller_service.register_seller(
            user_id=1, shop_name="Test Shop",
            address="Test Address", phone="0912345678", city="Addis Ababa"
        )
        assert await seller_service.reject_seller(seller_id, "test reason")
        seller = await seller_service.get_seller_by_id(seller_id)
        assert seller['status'] == 'rejected'


@pytest.fixture
async def item_service():
    """Create item service with test database."""
    from src.services import ItemService
    db = Database("data/test_item.db")
    await db.init()
    
    # Setup: create seller and user
    await db.execute(
        "INSERT INTO users (telegram_id, first_name, role) VALUES (?, ?, ?)",
        (1, "Test", "seller")
    )
    await db.execute(
        "INSERT INTO sellers (user_id, shop_name, address, phone, city, status) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Test Shop", "Test Addr", "0912345678", "Addis Ababa", "approved")
    )
    
    yield ItemService(db)
    import os
    if os.path.exists("data/test_item.db"):
        os.remove("data/test_item.db")


@pytest.mark.asyncio
class TestItemService:
    
    async def test_add_item(self, item_service):
        """Test adding an item."""
        success, item_id = await item_service.add_item(
            seller_id=1, category_id=1,
            name_en="Tomato", name_am="ቲማቲም",
            price=80.0, unit="kg"
        )
        assert success is True
        assert item_id > 0
    
    async def test_search_items(self, item_service):
        """Test searching for items."""
        await item_service.add_item(
            seller_id=1, category_id=1,
            name_en="Tomato", name_am="ቲማቲም",
            price=80.0, unit="kg"
        )
        items, total = await item_service.search_items(query="tomato", limit=10)
        assert total >= 1
    
    async def test_haversine_distance(self, item_service):
        """Test distance calculation."""
        dist = item_service._haversine_distance(9.0, 38.7, 9.1, 38.8)
        assert 0 < dist < 20  # Should be within reasonable range
    
    async def test_get_price_history(self, item_service):
        """Test getting price history."""
        success, item_id = await item_service.add_item(
            seller_id=1, category_id=1,
            name_en="Tomato", name_am="ቲማቲም",
            price=80.0, unit="kg"
        )
        history = await item_service.get_price_history(item_id, days=30)
        assert len(history) >= 1