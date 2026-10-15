"""Tests for localization."""
import pytest
from src.locales import i18n
from src.locales.en.messages import Messages as EnMessages
from src.locales.am.messages import Messages as AmMessages


class TestLocalization:
    
    def test_supported_languages(self):
        """Test that supported languages are correctly defined."""
        assert 'en' in i18n.SUPPORTED_LANGUAGES
        assert 'am' in i18n.SUPPORTED_LANGUAGES
    
    def test_get_message_english(self):
        """Test retrieving English message."""
        msg = i18n.get("WELCOME", "en")
        assert "Welcome" in msg
    
    def test_get_message_amharic(self):
        """Test retrieving Amharic message."""
        msg = i18n.get("WELCOME", "am")
        assert "አዲስ" in msg
    
    def test_fallback_to_default(self):
        """Test fallback to English when language not available."""
        msg = i18n.get("WELCOME", "fr")
        assert "Welcome" in msg
    
    def test_is_supported(self):
        """Test language support check."""
        assert i18n.is_supported("en") is True
        assert i18n.is_supported("am") is True
        assert i18n.is_supported("fr") is False
    
    def test_get_language_name(self):
        """Test language name display."""
        assert i18n.get_language_name("en") == "English"
        assert i18n.get_language_name("am") == "አማርኛ"