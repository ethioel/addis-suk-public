"""Pytest configuration and shared fixtures."""
import os
import sys
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ.setdefault("BOT_TOKEN", "123456789:AAH_test_token_for_testing")
os.environ.setdefault("ADMIN_IDS", "999999999")


@pytest.fixture
def test_db_path():
    """Provide test database path."""
    return "data/test_pytest.db"


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test database after each test."""
    yield
    test_db = Path("data/test_pytest.db")
    if test_db.exists():
        test_db.unlink()
    test_db2 = Path("data/test.db")
    if test_db2.exists():
        test_db2.unlink()