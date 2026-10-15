"""Tests for keyboard builders."""
import pytest
from aiogram.types import InlineKeyboardMarkup
from src.keyboards import (
    main_menu, language_selector, search_keyboard,
    seller_keyboard, admin_keyboard, yes_no_keyboard,
    subscription_keyboard, featured_listing_keyboard, create_keyboard
)


class TestKeyboards:
    
    def test_main_menu_english(self):
        """Test main menu keyboard in English."""
        kb = main_menu('en')
        assert isinstance(kb, InlineKeyboardMarkup)
        assert len(kb.inline_keyboard) > 0
    
    def test_main_menu_amharic(self):
        """Test main menu keyboard in Amharic."""
        kb = main_menu('am')
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_language_selector(self):
        """Test language selector keyboard."""
        kb = language_selector()
        assert isinstance(kb, InlineKeyboardMarkup)
        # Should have at least 2 language buttons + cancel
        assert len(kb.inline_keyboard) >= 2
    
    def test_search_keyboard(self):
        """Test search keyboard."""
        kb = search_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_seller_keyboard(self):
        """Test seller keyboard."""
        kb = seller_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_admin_keyboard(self):
        """Test admin keyboard."""
        kb = admin_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_yes_no_keyboard(self):
        """Test yes/no keyboard."""
        kb = yes_no_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_subscription_keyboard(self):
        """Test subscription keyboard."""
        kb = subscription_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_featured_listing_keyboard(self):
        """Test featured listing keyboard."""
        kb = featured_listing_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)
    
    def test_create_keyboard_with_rows(self):
        """Test create_keyboard with rows."""
        rows = [
            [("Button 1", "btn1"), ("Button 2", "btn2")],
            [("Button 3", "btn3")],
        ]
        kb = create_keyboard(rows)
        assert isinstance(kb, InlineKeyboardMarkup)
        assert len(kb.inline_keyboard) == 2