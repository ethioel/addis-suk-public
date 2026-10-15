"""Tests for user service."""
import pytest
from src.models.database import Database
from src.services import UserService


@pytest.fixture
async def user_service():
    """Create user service with test database."""
    db = Database("data/test_service.db")
    await db.init()
    yield UserService(db)
    import os
    if os.path.exists("data/test_service.db"):
        os.remove("data/test_service.db")


@pytest.mark.asyncio
class TestUserService:
    
    async def test_get_or_create_user(self, user_service):
        """Test user creation."""
        user = await user_service.get_or_create_user(
            telegram_id=999,
            first_name="Test User"
        )
        assert user['telegram_id'] == 999
        assert user['first_name'] == "Test User"
    
    async def test_get_existing_user(self, user_service):
        """Test retrieving existing user."""
        user1 = await user_service.get_or_create_user(
            telegram_id=999,
            first_name="Test User"
        )
        user2 = await user_service.get_or_create_user(
            telegram_id=999,
            first_name="Test User"
        )
        assert user1['id'] == user2['id']
    
    async def test_update_user_language(self, user_service):
        """Test language update."""
        await user_service.get_or_create_user(telegram_id=999, first_name="Test")
        assert await user_service.update_user_language(999, "am")
        user = await user_service.db.fetchone("SELECT language FROM users WHERE telegram_id = 999")
        assert user['language'] == "am"
    
    async def test_subscription_check(self, user_service):
        """Test subscription info retrieval."""
        user = await user_service.get_or_create_user(telegram_id=999, first_name="Test")
        info = await user_service.get_user_subscription_info(999)
        assert info['tier'] == 'free'
        assert info['is_premium'] == False
    
    async def test_set_premium(self, user_service):
        """Test setting user as premium."""
        await user_service.get_or_create_user(telegram_id=999, first_name="Test")
        assert await user_service.set_user_premium(999, months=1)
        info = await user_service.get_user_subscription_info(999)
        assert info['is_premium'] == True
        assert info['tier'] == 'premium'