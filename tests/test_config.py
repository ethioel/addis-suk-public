"""Tests for configuration."""
import pytest
from src.config import config, Config
from src.locales import i18n as i18n


class TestConfig:
    
    def test_config_exists(self):
        """Test that config loads."""
        assert config is not None
    
    def test_bot_token_required(self):
        """Test that BOT_TOKEN is required."""
        assert config.BOT_TOKEN is not None
    
    def test_admin_ids_is_list(self):
        """Test that ADMIN_IDS is a list."""
        assert isinstance(config.ADMIN_IDS, list)
    
    def test_prices_are_positive(self):
        """Test that all prices are positive."""
        assert config.BUYER_PREMIUM_PRICE > 0
        assert config.SELLER_PREMIUM_PRICE > 0
        assert config.FEATURED_LISTING_PRICE > 0
    
    def test_limits_are_positive(self):
        """Test that limits are positive."""
        assert config.FREE_SEARCH_LIMIT > 0
        assert config.FREE_ITEMS_LIMIT > 0
        assert config.PREMIUM_ALERTS_LIMIT > 0
    
    def test_cities_loaded(self):
        """Test that cities are loaded."""
        assert len(config.CITIES) > 0
        assert "Addis Ababa" in config.CITIES
    
    def test_sub_cities_loaded(self):
        """Test that Addis sub-cities are loaded."""
        assert len(config.ADDIS_SUB_CITIES) > 0
    
    def test_default_location(self):
        """Test default location is Addis Ababa."""
        assert config.DEFAULT_LATITUDE == 9.0320
        assert config.DEFAULT_LONGITUDE == 38.7529


class TestConfigDefaults:
    """Test default configuration values."""
    
    def test_supported_languages(self):
        """Test supported languages."""
        assert 'en' in i18n.SUPPORTED_LANGUAGES
        assert 'am' in i18n.SUPPORTED_LANGUAGES